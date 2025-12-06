import json, os, base64, sys, uuid, jwt
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
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
# CHECK KEYS
# -----------------------------
if not os.path.exists(PRIVATE_KEY_PATH) or not os.path.exists(PUBLIC_KEY_PATH):
    print("Erreur : clés manquantes. Générez-les avec generate_keys.py.")
    sys.exit(1)

with open(PRIVATE_KEY_PATH, "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(f.read(), password=None)

with open(PUBLIC_KEY_PATH, "rb") as f:
    PUBLIC_KEY = serialization.load_pem_public_key(f.read())

os.makedirs(DIPLOMAS_DIR, exist_ok=True)

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
def get_diploma(id):
    path = os.path.join(DIPLOMAS_DIR, f"{id}.json")
    if not os.path.exists(path):
        return jsonify({"error": "unknown diploma"}), 404

    with open(path) as f:
        return jsonify(json.load(f))

# -----------------------------
# VERIFY
# -----------------------------
@app.route("/verify", methods=["POST"])
def verify():
    diploma = request.json

    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r") as f:
            registry = json.load(f)
        for d in registry["diplomas"]:
            if d["filename"] == f"{diploma['id']}.json" and d.get("revoked"):
                return jsonify({"valid": False, "reason": "revoked"})

    signature = base64.b64decode(diploma["signature"])
    unsigned = diploma.copy()
    del unsigned["signature"]
    payload = json.dumps(unsigned, sort_keys=True).encode()

    try:
        PUBLIC_KEY.verify(signature, payload)
        return jsonify({"valid": True})
    except Exception:
        return jsonify({"valid": False})

# -----------------------------
# REVOKE
# -----------------------------
@app.route("/revoke", methods=["POST"])
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
def list_diplomas():
    if not os.path.exists(REGISTRY_FILE):
        return jsonify({"diplomas": []})

    with open(REGISTRY_FILE, "r") as f:
        return jsonify(json.load(f)["diplomas"])

# -----------------------------
# DOWNLOAD
# -----------------------------
@app.route("/download/<filename>", methods=["GET"])
def download_diploma(filename):
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
