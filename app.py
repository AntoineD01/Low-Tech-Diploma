import json, os, base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from datetime import datetime
import uuid
import sys

app = Flask(__name__)
CORS(app)

# Update the paths to be relative to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
clé_publique = os.path.join(script_dir, "keys", "public_key.pem")
clé_privée = os.path.join(script_dir, "keys", "private_key.pem")

# Vérifier si les fichiers de clés existent
if not os.path.exists(clé_privée) or not os.path.exists(clé_publique):
    print("Erreur : Un ou plusieurs fichiers de clés sont manquants. Veuillez générer les clés en utilisant 'generate_keys.py'.")
    sys.exit(1)

# Charger la clé privée et publique
with open(clé_privée, "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(f.read(), password=None)

with open(clé_publique, "rb") as f:
    PUBLIC_KEY = serialization.load_pem_public_key(f.read())

# -------------------------------------------
# 1. Émission d'un diplôme
# -------------------------------------------
@app.route("/issue", methods=["POST"])
def issue():
    data = request.json
    
    # données minimales
    diploma = {
        "id": str(uuid.uuid4()),
        "student_name": data.get("student_name"),
        "degree_name": data.get("degree_name"),
        "issued_at": datetime.utcnow().isoformat() + "Z"
    }

    # Canonicalisation JSON
    payload = json.dumps(diploma, sort_keys=True).encode()

    # Signature
    signature = PRIVATE_KEY.sign(payload)
    diploma["signature"] = base64.b64encode(signature).decode()

    # Sauvegarde local
    path = f"diplomas/{diploma['id']}.json"
    with open(path, "w") as f:
        json.dump(diploma, f, indent=2)

    # Mettre à jour le registre
    registry = {"diplomas": []}
    if os.path.exists("registry.json"):
        with open("registry.json", "r") as f:
            registry = json.load(f)

    registry["diplomas"].append({
        "filename": f"{diploma['id']}.json",
        "student_name": diploma["student_name"],
        "degree_name": diploma["degree_name"],
        "issued_at": diploma["issued_at"],
        "revoked": False
    })

    with open("registry.json", "w") as f:
        json.dump(registry, f, indent=2)

    return jsonify({
        "status": "ok",
        "diploma_id": diploma["id"],
        "download_url": f"/diploma/{diploma['id']}"
    })


# -------------------------------------------
# 2. Récupération d'un diplôme
# -------------------------------------------
@app.route("/diploma/<id>", methods=["GET"])
def get_diploma(id):
    path = f"diplomas/{id}.json"
    if not os.path.exists(path):
        return jsonify({"error": "unknown diploma"}), 404
        
    with open(path) as f:
        diploma = json.load(f)
        
    return jsonify(diploma)


# -------------------------------------------
# 3. Vérification d'un diplôme
# -------------------------------------------
@app.route("/verify", methods=["POST"])
def verify():
    diploma = request.json
    
    signature = base64.b64decode(diploma["signature"])
    
    # Retirer la signature avant vérification
    unsigned = diploma.copy()
    del unsigned["signature"]
    payload = json.dumps(unsigned, sort_keys=True).encode()

    try:
        PUBLIC_KEY.verify(signature, payload)
        return jsonify({
            "valid": True,
            "reason": "signature valid",
            "diploma_id": diploma["id"],
            "student_name": diploma["student_name"]
        })

    except Exception:
        return jsonify({"valid": False, "reason": "invalid signature"})
    
# -------------------------------------------
# 4. Révocation d'un diplôme
# -------------------------------------------
@app.route("/revoke", methods=["POST"])
def revoke():
    data = request.json
    diploma_id = data.get("id")
    
    # Charger le registre
    with open("registry.json", "r") as f:
        registry = json.load(f)
    
    found = False
    for d in registry["diplomas"]:
        if d["filename"] == f"{diploma_id}.json":
            d["revoked"] = True
            found = True
            path = os.path.join("diplomas", d["filename"])
            if os.path.exists(path):
                os.remove(path)
            break
    
    if not found:
        return jsonify({"status": "error", "message": "Diploma not found"}), 404
    
    # Sauvegarder le registre
    with open("registry.json", "w") as f:
        json.dump(registry, f, indent=2)
    
    return jsonify({"status": "ok", "message": "Diploma revoked"})

# -------------------------------------------
# 5. Lister les diplômes
# -------------------------------------------
@app.route("/list", methods=["GET"])
def list_diplomas():
    if not os.path.exists("registry.json"):
        return jsonify({"diplomas": []})
    
    with open("registry.json", "r") as f:
        registry = json.load(f)
    
    return jsonify(registry["diplomas"])

# -------------------------------------------
# 5. Télécharger un diplôme (fichier)
# -------------------------------------------
@app.route("/download/<filename>", methods=["GET"])
def download_diploma(filename):
    return send_from_directory("diplomas", filename)

# -------------------------------------------
# Lancer le serveur
# -------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
