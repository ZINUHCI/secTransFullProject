from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import base64, requests, os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")

    # -----------------------------
    # ENCRYPT AND DECRYPT MESSAGE (AES + RSA) HELPERS
    # -----------------------------
def encrypt_for_recipient(self, plaintext, recipient_username):
    headers = {"Authorization": f"Bearer {self.token}"}
    res = requests.get(f"{SERVER_URL}/pubKey/public-key/{recipient_username}", headers=headers)
    if res.status_code != 200:
        raise Exception("Recipient public key not found")

    recipient_public_key = RSA.import_key(res.json()["publicKey"])

    aes_key = get_random_bytes(32)
    cipher_aes = AES.new(aes_key, AES.MODE_GCM)
    ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext.encode() if isinstance(plaintext, str) else plaintext)

    cipher_rsa = PKCS1_OAEP.new(recipient_public_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)

    result =  {
        "encryptedAesKeyB64": base64.b64encode(encrypted_aes_key).decode(),
        "nonceB64": base64.b64encode(cipher_aes.nonce).decode(),
        "ciphertextB64": base64.b64encode(ciphertext).decode(),
            "tagB64": base64.b64encode(tag).decode(),
    }

    return result
