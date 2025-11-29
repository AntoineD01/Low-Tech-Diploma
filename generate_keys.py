from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import os

# Ensure the keys directory exists
keys_dir = "keys"
os.makedirs(keys_dir, exist_ok=True)

# Generate private and public keys
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Save the private key
with open(os.path.join(keys_dir, "private_key.pem"), "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Save the public key
with open(os.path.join(keys_dir, "public_key.pem"), "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("Keys generated successfully!")