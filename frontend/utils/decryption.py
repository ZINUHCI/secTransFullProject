from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import base64

def decrypt_message_payload(self, msg_obj):
    """
    Decrypts a single message object from the server.
    Returns plaintext bytes (for text messages, decode to string).
    """
    if not self.private_key:
        raise Exception("No private key available to decrypt")

    enc_key_b64 = msg_obj.get("encryptedAesKeyB64")
    nonce_b64 = msg_obj.get("nonceB64")
    ct_b64 = msg_obj.get("ciphertextB64")
    tag_b64 = msg_obj.get("tagB64")

    print(msg_obj)

    if not (enc_key_b64 and nonce_b64 and ct_b64 and tag_b64):
        raise Exception("Missing fields for decryption")

    encrypted_aes_key = base64.b64decode(enc_key_b64)
    nonce = base64.b64decode(nonce_b64)
    ciphertext = base64.b64decode(ct_b64)
    tag = base64.b64decode(tag_b64)

    # RSA decrypt AES key using private key
    priv = RSA.import_key(self.private_key)
    rsa_cipher = PKCS1_OAEP.new(priv)
    aes_key = rsa_cipher.decrypt(encrypted_aes_key)

    # AES-GCM decrypt
    aes_cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    plaintext = aes_cipher.decrypt_and_verify(ciphertext, tag)  # raises ValueError if tag mismatch
    return plaintext