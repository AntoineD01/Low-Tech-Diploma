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

# Don't use static_url_path='' as it conflicts with React Router
# Let the catch-all route handle serving everything
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching in development
# Restrict CORS to specific origin (use '*' only for development)
CORS(app, origins=[ALLOWED_ORIGIN] if ALLOWED_ORIGIN != '*' else '*')

# -----------------------------
# ERROR HANDLERS
# -----------------------------
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with detailed debugging information"""
    error_info = {
        'error': '404 Not Found',
        'message': 'The requested resource was not found',
        'path': request.path,
        'method': request.method,
        'url': request.url,
        'referrer': request.referrer,
        'user_agent': str(request.user_agent),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Log to server console
    print("\n" + "="*80)
    print("❌ 404 ERROR DETAILS:")
    for key, value in error_info.items():
        print(f"  {key}: {value}")
    print("="*80 + "\n")
    
    # Return JSON for API requests, HTML for browser requests
    if request.path.startswith('/api/') or request.accept_mimetypes.accept_json:
        return jsonify(error_info), 404
    
    # For HTML requests, return a debug page
    return f"""
    <html>
        <head>
            <title>404 - Not Found</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 50px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ color: #d32f2f; }}
                .error-details {{ background: #f5f5f5; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                .error-details pre {{ margin: 0; overflow-x: auto; }}
                code {{ background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }}
            </style>
            <script>
                // Log error details to browser console
                console.error('404 Error Details:', {json.dumps(error_info, indent=2)});
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🔍 404 - Page Not Found</h1>
                <p>The requested page could not be found.</p>
                <div class="error-details">
                    <h3>Debug Information:</h3>
                    <pre>{json.dumps(error_info, indent=2)}</pre>
                </div>
                <p><a href="/">← Back to Home</a></p>
            </div>
        </body>
    </html>
    """, 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with debugging information"""
    error_info = {
        'error': '500 Internal Server Error',
        'message': str(error),
        'path': request.path,
        'method': request.method,
        'timestamp': datetime.utcnow().isoformat()
    }
    print("\n" + "="*80)
    print("❌ 500 ERROR:", str(error))
    print("="*80 + "\n")
    return jsonify(error_info), 500

# -----------------------------
# REQUEST LOGGING MIDDLEWARE
# -----------------------------
@app.before_request
def log_request():
    """Log all incoming requests before routing"""
    print("\n" + "🔵"*40, flush=True)
    print(f"📨 INCOMING REQUEST: {request.method} {request.path}", flush=True)
    print(f"   Full URL: {request.url}", flush=True)
    print(f"   Endpoint will be: {request.endpoint if hasattr(request, 'endpoint') else 'unknown'}", flush=True)
    print("🔵"*40 + "\n", flush=True)
    sys.stdout.flush()

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
    keys_collection = db.keys
    
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

DIPLOMAS_DIR = os.path.join(script_dir, "diplomas")
PDFS_DIR = os.path.join(script_dir, "pdfs")

# -----------------------------
# LOAD OR GENERATE KEYS FROM MONGODB
# -----------------------------
def load_or_generate_keys():
    """Load keys from MongoDB or generate new ones if they don't exist"""
    # Try to load existing keys from MongoDB
    key_doc = keys_collection.find_one({"key_id": "main"})
    
    if key_doc:
        print("Loading existing keys from MongoDB...")
        # Load keys from database
        private_key_pem = key_doc["private_key"].encode()
        public_key_pem = key_doc["public_key"].encode()
        
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        public_key = serialization.load_pem_public_key(public_key_pem)
        
        print("Keys loaded successfully from MongoDB!")
        return private_key, public_key
    else:
        print("No keys found in MongoDB. Generating new keys...")
        # Generate new keys
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        # Store keys in MongoDB
        keys_collection.insert_one({
            "key_id": "main",
            "private_key": private_key_pem,
            "public_key": public_key_pem,
            "created_at": datetime.utcnow().isoformat() + "Z"
        })
        
        print("Keys generated and stored in MongoDB successfully!")
        return private_key, public_key

PRIVATE_KEY, PUBLIC_KEY = load_or_generate_keys()

os.makedirs(DIPLOMAS_DIR, exist_ok=True)
os.makedirs(PDFS_DIR, exist_ok=True)

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
            
            # Support both "Bearer token" and raw token formats
            if token.startswith("Bearer "):
                token = token[7:]  # Remove "Bearer " prefix
            
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

Connectez-vous sur: {ALLOWED_ORIGIN}/login

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
# BULK ISSUE
# -----------------------------
@app.route("/bulk_issue", methods=["POST"])
@auth_required("school")
def bulk_issue():
    # Lazy import pandas to avoid startup issues
    try:
        import pandas as pd
    except ImportError:
        return jsonify({"error": "Bulk import feature is not available. pandas library is not installed."}), 503
    
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Check file extension
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        return jsonify({"error": "Only CSV and Excel files are supported"}), 400
    
    try:
        # Read file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Validate required columns
        required_columns = ['student_name', 'student_email', 'degree_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({
                "error": f"Missing required columns: {', '.join(missing_columns)}",
                "hint": "Required columns: student_name, student_email, degree_name"
            }), 400
        
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        # Process each row
        for index, row in df.iterrows():
            try:
                student_name = str(row['student_name']).strip()
                student_email = str(row['student_email']).strip()
                degree_name = str(row['degree_name']).strip()
                
                # Skip empty rows
                if not student_name or student_name == 'nan':
                    continue
                
                results["total"] += 1
                
                # Check if user already exists
                existing_user = users_collection.find_one({"username": student_name})
                account_created = False
                student_password = None
                
                if not existing_user:
                    # Generate password
                    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
                    student_password = ''.join(secrets.choice(alphabet) for i in range(12))
                    
                    # Create student account
                    users_collection.insert_one({
                        "username": student_name,
                        "password": generate_password_hash(student_password),
                        "role": "student",
                        "email": student_email
                    })
                    account_created = True
                
                # Create diploma
                diploma = {
                    "id": str(uuid.uuid4()),
                    "student_name": student_name,
                    "degree_name": degree_name,
                    "issued_at": datetime.utcnow().isoformat() + "Z",
                    "revoked": False
                }
                
                payload = json.dumps(diploma, sort_keys=True).encode()
                signature = PRIVATE_KEY.sign(payload)
                diploma["signature"] = base64.b64encode(signature).decode()
                
                # Save to MongoDB
                diplomas_collection.insert_one(diploma)
                
                # Generate PDF
                pdf_path = None
                try:
                    pdf_path = generate_diploma_pdf(diploma)
                except Exception as e:
                    print(f"Failed to generate PDF for {student_name}: {e}")
                
                # Send email
                email_sent = False
                try:
                    if app.config['MAIL_USERNAME']:
                        msg = Message(
                            subject=f"Votre diplome: {degree_name}",
                            recipients=[student_email],
                            body=f"""Bonjour {student_name},

Felicitations ! Votre diplome "{degree_name}" a ete emis avec succes.

{'Votre compte a ete cree. Voici vos identifiants de connexion :' if account_created else 'Vous pouvez vous connecter avec vos identifiants existants :'}

Nom d'utilisateur: {student_name}
{('Mot de passe: ' + student_password) if account_created and student_password else ''}

Connectez-vous sur: {ALLOWED_ORIGIN}/login

Veuillez trouver votre diplome en piece jointe au format PDF.

Cordialement,
L'equipe Low-Tech Diploma
"""
                        )
                        
                        if pdf_path and os.path.exists(pdf_path):
                            with open(pdf_path, 'rb') as fp:
                                msg.attach(
                                    f"diplome_{student_name}.pdf",
                                    "application/pdf",
                                    fp.read()
                                )
                        
                        mail.send(msg)
                        email_sent = True
                except Exception as e:
                    print(f"Failed to send email to {student_email}: {e}")
                
                results["success"] += 1
                results["details"].append({
                    "student": student_name,
                    "status": "success",
                    "diploma_id": diploma["id"],
                    "email_sent": email_sent
                })
                
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "student": str(row.get('student_name', f'Row {index + 1}')),
                    "status": "failed",
                    "error": str(e)
                })
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

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
# DEBUG ROUTES (can remove in production)
# -----------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "dist_exists": os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')),
        "message": "Backend is running"
    })

@app.route("/debug/routes", methods=["GET"])
def debug_routes():
    """List all registered routes for debugging"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': sorted(rule.methods - {'HEAD', 'OPTIONS'}),
            'path': str(rule)
        })
    return jsonify(sorted(routes, key=lambda x: x['path']))

# -----------------------------
# SERVE REACT FRONTEND
# -----------------------------
@app.route('/', defaults={'path': ''}, methods=['GET', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'HEAD'])
def serve_react(path):
    """Serve React frontend in production - handles all GET requests for SPA routing"""
    dist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
    index_path = os.path.join(dist_path, 'index.html')
    
    # Enhanced debug logging with forced flush
    print("\n" + "-"*80, flush=True)
    print(f"📍 ROUTE REQUEST: {request.method} /{path}", flush=True)
    print(f"   Full URL: {request.url}", flush=True)
    print(f"   Referrer: {request.referrer}", flush=True)
    print(f"   Accept: {request.headers.get('Accept', 'N/A')[:100]}", flush=True)
    print(f"📂 Dist path: {dist_path}", flush=True)
    print(f"   Dist exists: {os.path.exists(dist_path)}", flush=True)
    print(f"📄 Index path: {index_path}", flush=True)
    print(f"   Index exists: {os.path.exists(index_path)}", flush=True)
    sys.stdout.flush()
    
    # Serve React app if dist folder exists (production)
    if os.path.exists(dist_path):
        # Check if it's a static file request (js, css, images, etc.)
        if path and '.' in path.split('/')[-1]:
            file_path = os.path.join(dist_path, path)
            print(f"🔍 Checking static file: {file_path}", flush=True)
            if os.path.exists(file_path):
                print(f"✅ Serving static file: {path}", flush=True)
                print("-"*80 + "\n", flush=True)
                sys.stdout.flush()
                return send_from_directory(dist_path, path)
            else:
                print(f"❌ Static file NOT FOUND: {file_path}", flush=True)
                print(f"   Available files in dist: {os.listdir(dist_path)[:10]}", flush=True)
                print("-"*80 + "\n", flush=True)
                sys.stdout.flush()
                # Return error with debugging info
                error_data = {
                    'error': 'Static file not found',
                    'path': path,
                    'file_path': file_path,
                    'dist_contents': os.listdir(dist_path)[:20]
                }
                print(f"⚠️ RETURNING 404 for static file")
                return jsonify(error_data), 404
        
        # For all other routes (including /verify, /issue, etc.), serve index.html for React Router
        if os.path.exists(index_path):
            print(f"✅ Serving index.html for SPA route: /{path}", flush=True)
            print("-"*80 + "\n", flush=True)
            sys.stdout.flush()
            return send_from_directory(dist_path, 'index.html')
        else:
            print(f"❌ CRITICAL: index.html not found at {index_path}", flush=True)
            print("-"*80 + "\n", flush=True)
            sys.stdout.flush()
            return jsonify({
                'error': 'index.html not found',
                'index_path': index_path,
                'dist_exists': os.path.exists(dist_path),
                'dist_contents': os.listdir(dist_path) if os.path.exists(dist_path) else []
            }), 404
    else:
        # Development mode - show message
        return f"""
        <html>
            <body style="font-family: Arial; padding: 50px; text-align: center;">
                <h1>Low-Tech Diploma Platform</h1>
                <p>Backend API is running on port {os.getenv('PORT', 5000)}</p>
                <p style="color: red;">⚠️ dist/ folder not found at: {dist_path}</p>
                <p>To run the frontend in development mode:</p>
                <pre style="background: #f4f4f4; padding: 20px; border-radius: 5px; display: inline-block; text-align: left;">
npm install
npm run build</pre>
            </body>
        </html>
        """

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    # Get port from environment variable (for Koyeb, Heroku, etc.) or use 5000
    port = int(os.getenv('PORT', 5000))
    # Disable debug in production
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting Flask app on port {port}")
    if os.path.exists('dist'):
        print("✅ Serving React frontend from dist/")
    else:
        print("⚠️  No dist/ folder found - running in API-only mode")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
