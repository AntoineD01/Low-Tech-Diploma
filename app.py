import json, os, base64, sys, uuid, jwt
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

SECRET = "SUPER_SECRET_KEY_CHANGE_ME"

app = Flask(__name__)
CORS(app)

# -----------------------------
# BASE PATHS (✅ CORRECT)
# -----------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))

KEYS_DIR = os.path.join(script_dir, "keys")
DIPLOMAS_DIR = os.path.join(script_dir, "diplomas")
REGISTRY_FILE = os.path.join(script_dir, "registry.json")
USERS_FILE = os.path.join(script_dir, "users.json")

PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, "public_key.pem")
PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, "private_key.pem")

# -----------------------------
# CHECK AND GENERATE KEYS IF NEEDED
# -----------------------------
os.makedirs(KEYS_DIR, exist_ok=True)

if not os.path.exists(PRIVATE_KEY_PATH) or not os.path.exists(PUBLIC_KEY_PATH):
    print("Keys missing. Generating automatically...")
    # Generate private and public keys
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Save the private key
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Save the public key
    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print("Keys generated successfully!")

with open(PRIVATE_KEY_PATH, "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(f.read(), password=None)

with open(PUBLIC_KEY_PATH, "rb") as f:
    PUBLIC_KEY = serialization.load_pem_public_key(f.read())

os.makedirs(DIPLOMAS_DIR, exist_ok=True)

# -----------------------------
# WEB PAGES ROUTES
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login-page")
def login_page():
    return render_template("login.html")

@app.route("/issue-page")
def issue_page():
    return render_template("issue.html")

@app.route("/verify-page")
def verify_page():
    return render_template("verify.html")

@app.route("/my-diplomas-page")
def my_diplomas_page():
    return render_template("my_diplomas.html")

@app.route("/all-diplomas-page")
def all_diplomas_page():
    return render_template("all_diplomas.html")

# -----------------------------
# AUTH DECORATOR
# -----------------------------
def auth_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"error": "Missing token"}), 401
            try:
                decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
            except Exception:
                return jsonify({"error": "Invalid token"}), 401

            if role and decoded.get("role") != role:
                return jsonify({"error": "Forbidden"}), 403

            request.user = decoded
            return f(*args, **kwargs)
        return wrapper
    return decorator

# -----------------------------
# ISSUE
# -----------------------------
@app.route("/issue", methods=["POST"])
@auth_required("school")
def issue():
    data = request.json

    diploma = {
        "id": str(uuid.uuid4()),
        "student_name": data.get("student_name"),
        "degree_name": data.get("degree_name"),
        "issued_at": datetime.utcnow().isoformat() + "Z"
    }

    payload = json.dumps(diploma, sort_keys=True).encode()
    signature = PRIVATE_KEY.sign(payload)
    diploma["signature"] = base64.b64encode(signature).decode()

    path = os.path.join(DIPLOMAS_DIR, f"{diploma['id']}.json")
    with open(path, "w") as f:
        json.dump(diploma, f, indent=2)

    registry = {"diplomas": []}
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r") as f:
            registry = json.load(f)

    registry["diplomas"].append({
        "filename": f"{diploma['id']}.json",
        "student_name": diploma["student_name"],
        "degree_name": diploma["degree_name"],
        "issued_at": diploma["issued_at"],
        "revoked": False
    })

    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)

    return jsonify({"status": "ok", "diploma_id": diploma["id"]})

# -----------------------------
# GET DIPLOMA
# -----------------------------
@app.route("/diploma/<id>", methods=["GET"])
@auth_required()
def get_diploma(id):
    filename = f"{id}.json"
    path = os.path.join(DIPLOMAS_DIR, filename)

    if not os.path.exists(path):
        return jsonify({"error": "unknown diploma"}), 404

    with open(path) as f:
        diploma = json.load(f)

    user = request.user

    # School can access everything
    if user["role"] == "school":
        return jsonify(diploma)

    # Student only their own
    if user["role"] == "student":
        if user["username"] != diploma["student_name"]:
            return jsonify({"error": "Forbidden"}), 403

    return jsonify(diploma)


# -----------------------------
# VERIFY
# -----------------------------
@app.route("/verify", methods=["POST"])
def verify():
    diploma = request.json

    # Load the registry
    found = False
    revoked = False
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r") as f:
            registry = json.load(f)
        for d in registry["diplomas"]:
            if d["filename"] == f"{diploma['id']}.json":
                found = True
                revoked = d.get("revoked", False)
                break

    if not found:
        return jsonify({"valid": False, "reason": "unknown diploma"})

    if revoked:
        return jsonify({"valid": False, "reason": "revoked diploma"})

    # Verify the signature
    signature = base64.b64decode(diploma["signature"])
    unsigned = diploma.copy()
    del unsigned["signature"]
    payload = json.dumps(unsigned, sort_keys=True).encode()

    try:
        PUBLIC_KEY.verify(signature, payload)
        return jsonify({"valid": True})
    except Exception:
        return jsonify({"valid": False, "reason": "invalid signature"})


# -----------------------------
# REVOKE
# -----------------------------
@app.route("/revoke", methods=["POST"])
@auth_required("school")
def revoke():
    data = request.json
    diploma_id = data.get("id")

    with open(REGISTRY_FILE, "r") as f:
        registry = json.load(f)

    for d in registry["diplomas"]:
        if d["filename"] == f"{diploma_id}.json":
            d["revoked"] = True
            file_path = os.path.join(DIPLOMAS_DIR, d["filename"])
            if os.path.exists(file_path):
                os.remove(file_path)
            break

    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)

    return jsonify({"status": "ok"})

# -----------------------------
# LIST
# -----------------------------
@app.route("/list", methods=["GET"])
@auth_required()
def list_diplomas():
    if not os.path.exists(REGISTRY_FILE):
        return jsonify({"diplomas": []})

    with open(REGISTRY_FILE, "r") as f:
        registry = json.load(f)

    user = request.user

    if user["role"] == "school":
        # School sees all diplomas
        diplomas = registry["diplomas"]
    elif user["role"] == "student":
        # Student sees only their diplomas
        diplomas = [d for d in registry["diplomas"] if d["student_name"] == user["username"]]
    else:
        diplomas = []

    return jsonify(diplomas)

# -----------------------------
# DOWNLOAD
# -----------------------------
@app.route("/download/<filename>", methods=["GET"])
@auth_required()
def download_diploma(filename):
    if not os.path.exists(REGISTRY_FILE):
        return jsonify({"error": "registry missing"}), 500

    with open(REGISTRY_FILE, "r") as f:
        registry = json.load(f)

    entry = next((d for d in registry["diplomas"] if d["filename"] == filename), None)
    if not entry:
        return jsonify({"error": "not found"}), 404

    user = request.user

    # School can download everything
    if user["role"] == "school":
        return send_from_directory(DIPLOMAS_DIR, filename)

    # Student can download ONLY their diploma
    if user["role"] == "student":
        if user["username"] != entry["student_name"]:
            return jsonify({"error": "Forbidden"}), 403

    return send_from_directory(DIPLOMAS_DIR, filename)


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    with open(USERS_FILE, "r") as f:
        users = json.load(f)["users"]

    for user in users:
        if user["username"] == data["username"] and user["password"] == data["password"]:
            token = jwt.encode(
                {"username": user["username"], "role": user["role"]},
                SECRET,
                algorithm="HS256"
            )
            return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
