import json, os, base64, sys, uuid, jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from pymongo import MongoClient
from pymongo.server_api import ServerApi

SECRET = os.getenv('JWT_SECRET')
MONGO_URI = os.getenv('MONGO_URI')
ALLOWED_ORIGIN = os.getenv('ALLOWED_ORIGIN', '*')

# Validate required environment variables
if not SECRET:
    print("ERROR: JWT_SECRET environment variable is not set!")
    sys.exit(1)
if not MONGO_URI:
    print("ERROR: MONGO_URI environment variable is not set!")
    sys.exit(1)

app = Flask(__name__)
# Restrict CORS to specific origin (use '*' only for development)
CORS(app, origins=[ALLOWED_ORIGIN] if ALLOWED_ORIGIN != '*' else '*')

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
mail = Mail(app)

# -----------------------------
# MONGODB CONNECTION
# -----------------------------
try:
    # Add connection timeout settings
    client = MongoClient(
        MONGO_URI, 
        server_api=ServerApi('1'),
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    db = client.lowtechdiploma
    diplomas_collection = db.diplomas
    users_collection = db.users
    
    # Test connection with timeout
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    # Initialize default users if collection is empty
    if users_collection.count_documents({}) == 0:
        print("Initializing default users...")
        users_collection.insert_many([
            {"username": "school", "password": generate_password_hash("schoolpass"), "role": "school"},
            {"username": "alice", "password": generate_password_hash("alicepass"), "role": "student"}
        ])
        print("Default users created with hashed passwords!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    print("Please check your MONGO_URI environment variable and MongoDB Atlas network settings")
    sys.exit(1)

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
@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/login.html")
def login_page():
    return render_template("login.html")

@app.route("/issue.html")
def issue_page():
    return render_template("issue.html")

@app.route("/verify.html")
def verify_page():
    return render_template("verify.html")

@app.route("/my_diplomas.html")
def my_diplomas_page():
    return render_template("my_diplomas.html")

@app.route("/all_diplomas.html")
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
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError:
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
    student_name = data.get("student_name")
    student_email = data.get("student_email")
    student_password = data.get("student_password")

    # Check if user already exists
    existing_user = users_collection.find_one({"username": student_name})
    account_created = False
    
    if not existing_user:
        # Create new student account
        users_collection.insert_one({
            "username": student_name,
            "password": generate_password_hash(student_password),
            "role": "student",
            "email": student_email
        })
        print(f"New student account created: {student_name}")
        account_created = True
    else:
        print(f"User {student_name} already exists, skipping account creation")

    diploma = {
        "id": str(uuid.uuid4()),
        "student_name": student_name,
        "degree_name": data.get("degree_name"),
        "issued_at": datetime.utcnow().isoformat() + "Z",
        "revoked": False
    }

    payload = json.dumps(diploma, sort_keys=True).encode()
    signature = PRIVATE_KEY.sign(payload)
    diploma["signature"] = base64.b64encode(signature).decode()

    # Save to MongoDB
    diplomas_collection.insert_one(diploma)

    # Send email to student
    try:
        if app.config['MAIL_USERNAME']:  # Only send if mail is configured
            msg = Message(
                subject=f"Votre diplôme: {data.get('degree_name')}",
                recipients=[student_email],
                body=f"""Bonjour {student_name},

Félicitations ! Votre diplôme "{data.get('degree_name')}" a été émis avec succès.

{'Votre compte a été créé. Voici vos identifiants de connexion :' if account_created else 'Vous pouvez vous connecter avec vos identifiants existants :'}

Nom d\'utilisateur: {student_name}
{'Mot de passe: ' + student_password if account_created else ''}

Connectez-vous sur: {ALLOWED_ORIGIN}/login.html

Vous pourrez consulter et télécharger votre diplôme dans la section "Mes diplômes".

Cordialement,
L'équipe Low-Tech Diploma
"""
            )
            mail.send(msg)
            print(f"Email sent to {student_email}")
            email_sent = True
        else:
            print("Mail not configured, skipping email")
            email_sent = False
    except Exception as e:
        print(f"Failed to send email: {e}")
        email_sent = False

    return jsonify({
        "status": "ok", 
        "diploma_id": diploma["id"], 
        "account_created": account_created,
        "email_sent": email_sent
    })

# -----------------------------
# GET DIPLOMA
# -----------------------------
@app.route("/diploma/<id>", methods=["GET"])
@auth_required()
def get_diploma(id):
    diploma = diplomas_collection.find_one({"id": id}, {"_id": 0})

    if not diploma:
        return jsonify({"error": "unknown diploma"}), 404

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

    # Check if diploma exists in database
    db_diploma = diplomas_collection.find_one({"id": diploma.get("id")})
    
    if not db_diploma:
        return jsonify({"valid": False, "reason": "unknown diploma"})

    if db_diploma.get("revoked", False):
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

    # Mark diploma as revoked in MongoDB
    diplomas_collection.update_one(
        {"id": diploma_id},
        {"$set": {"revoked": True}}
    )

    return jsonify({"status": "ok"})

# -----------------------------
# LIST
# -----------------------------
@app.route("/list", methods=["GET"])
@auth_required()
def list_diplomas():
    user = request.user

    if user["role"] == "school":
        # School sees all diplomas
        diplomas = list(diplomas_collection.find({}, {"_id": 0}))
    elif user["role"] == "student":
        # Student sees only their diplomas
        diplomas = list(diplomas_collection.find({"student_name": user["username"]}, {"_id": 0}))
    else:
        diplomas = []

    return jsonify(diplomas)

# -----------------------------
# DOWNLOAD
# -----------------------------
@app.route("/download/<diploma_id>", methods=["GET"])
@auth_required()
def download_diploma(diploma_id):
    # Remove .json extension if present
    diploma_id = diploma_id.replace(".json", "")
    
    diploma = diplomas_collection.find_one({"id": diploma_id}, {"_id": 0})
    
    if not diploma:
        return jsonify({"error": "not found"}), 404

    user = request.user

    # School can download everything
    if user["role"] == "school":
        return jsonify(diploma)

    # Student can download ONLY their diploma
    if user["role"] == "student":
        if user["username"] != diploma["student_name"]:
            return jsonify({"error": "Forbidden"}), 403

    return jsonify(diploma)


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = users_collection.find_one({"username": data.get("username")})

    if user and check_password_hash(user["password"], data.get("password")):
        # Token expires in 24 hours
        token = jwt.encode(
            {
                "username": user["username"], 
                "role": user["role"],
                "exp": datetime.utcnow() + timedelta(hours=24)
            },
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
