import json, os, base64, sys, uuid, jwt, secrets, string, zipfile, io
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
from flask_cors import CORS
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

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
PDFS_DIR = os.path.join(script_dir, "pdfs")
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
os.makedirs(PDFS_DIR, exist_ok=True)

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
# GENERATE PDF DIPLOMA
# -----------------------------
def generate_diploma_pdf(diploma):
    """Generate a professional PDF diploma."""
    pdf_filename = f"{diploma['id']}.pdf"
    pdf_path = os.path.join(PDFS_DIR, pdf_filename)
    
    # Create PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Draw border
    c.setStrokeColor(colors.HexColor('#1a472a'))
    c.setLineWidth(3)
    c.rect(2*cm, 2*cm, width - 4*cm, height - 4*cm)
    
    # Inner decorative border
    c.setLineWidth(1)
    c.rect(2.3*cm, 2.3*cm, width - 4.6*cm, height - 4.6*cm)
    
    # Title
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor('#1a472a'))
    c.drawCentredString(width / 2, height - 5*cm, "DIPLÔME")
    
    # Subtitle
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 6.5*cm, "Ce document certifie que")
    
    # Student name
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor('#2e7d32'))
    c.drawCentredString(width / 2, height - 9*cm, diploma['student_name'])
    
    # Achievement text
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 11*cm, "a obtenu avec succès le diplôme de")
    
    # Degree name
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor('#1a472a'))
    c.drawCentredString(width / 2, height - 13*cm, diploma['degree_name'])
    
    # Date
    issue_date = datetime.fromisoformat(diploma['issued_at'].replace('Z', '+00:00'))
    date_str = issue_date.strftime("%d %B %Y")
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 16*cm, f"Délivré le {date_str}")
    
    # Diploma ID (small text at bottom)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 3*cm, f"ID: {diploma['id']}")
    
    # Signature section
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.black)
    c.drawString(width - 10*cm, 5*cm, "Signature de l'etablissement")
    c.line(width - 10*cm, 4.7*cm, width - 3*cm, 4.7*cm)
    
    # Low-Tech Diploma watermark
    c.setFont("Helvetica-BoldOblique", 40)
    c.setFillColor(colors.Color(0.9, 0.9, 0.9, alpha=0.3))
    c.saveState()
    c.translate(width / 2, height / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, "LOW-TECH DIPLOMA")
    c.restoreState()
    
    # Save PDF
    c.save()
    
    return pdf_path

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

    # Check if user already exists
    existing_user = users_collection.find_one({"username": student_name})
    account_created = False
    student_password = None
    
    if not existing_user:
        # Generate a secure random password (12 characters: letters, digits, special chars)
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        student_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        # Create new student account
        users_collection.insert_one({
            "username": student_name,
            "password": generate_password_hash(student_password),
            "role": "student",
            "email": student_email
        })
        print(f"New student account created: {student_name} with auto-generated password")
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

    # Generate PDF diploma
    pdf_path = None
    try:
        pdf_path = generate_diploma_pdf(diploma)
        print(f"PDF diploma generated: {pdf_path}")
    except Exception as e:
        print(f"Failed to generate PDF: {e}")

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
{('Mot de passe: ' + student_password) if account_created and student_password else ''}

Connectez-vous sur: {ALLOWED_ORIGIN}/login.html

Vous pourrez consulter et télécharger votre diplôme dans la section "Mes diplômes".

Veuillez trouver votre diplôme en pièce jointe au format PDF.

Cordialement,
L'équipe Low-Tech Diploma
"""
            )
            
            # Attach PDF diploma to email
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as fp:
                    msg.attach(
                        f"diplome_{student_name}.pdf",
                        "application/pdf",
                        fp.read()
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
        pass
    # Student can download ONLY their diploma
    elif user["role"] == "student":
        if user["username"] != diploma["student_name"]:
            return jsonify({"error": "Forbidden"}), 403
    
    # Create a zip file containing JSON and PDF
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add JSON file
        json_data = json.dumps(diploma, indent=2)
        zf.writestr(f"{diploma_id}.json", json_data)
        
        # Add PDF file
        pdf_path = os.path.join(PDFS_DIR, f"{diploma_id}.pdf")
        if not os.path.exists(pdf_path):
            # Generate PDF if it doesn't exist
            try:
                pdf_path = generate_diploma_pdf(diploma)
            except Exception as e:
                return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500
        
        with open(pdf_path, 'rb') as pdf_file:
            zf.writestr(f"diplome_{diploma['student_name']}.pdf", pdf_file.read())
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"diplome_{diploma['student_name']}_{diploma_id}.zip"
    )


# -----------------------------
# DOWNLOAD PDF
# -----------------------------
@app.route("/download_pdf/<diploma_id>", methods=["GET"])
@auth_required()
def download_pdf(diploma_id):
    diploma = diplomas_collection.find_one({"id": diploma_id}, {"_id": 0})
    
    if not diploma:
        return jsonify({"error": "not found"}), 404

    user = request.user

    # School can download everything
    if user["role"] == "school":
        pass
    # Student can download ONLY their diploma
    elif user["role"] == "student":
        if user["username"] != diploma["student_name"]:
            return jsonify({"error": "Forbidden"}), 403

    pdf_path = os.path.join(PDFS_DIR, f"{diploma_id}.pdf")
    
    if not os.path.exists(pdf_path):
        # Generate PDF if it doesn't exist
        try:
            pdf_path = generate_diploma_pdf(diploma)
        except Exception as e:
            return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500
    
    return send_file(pdf_path, as_attachment=True, download_name=f"diplome_{diploma['student_name']}_{diploma_id}.pdf")


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
