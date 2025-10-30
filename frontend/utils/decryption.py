from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import base64
import json

def decrypt_message_payload(self, msg_obj):
    """
    Decrypts both text and file payloads from an incoming message object.
    Returns:
        - For text messages: decoded UTF-8 string
        - For file messages: raw bytes
    """
    if not self.private_key:
        raise Exception("No private key available to decrypt message")

    try:
        enc_key_b64 = msg_obj.get("encryptedAesKeyB64")
        nonce_b64 = msg_obj.get("nonceB64")
        ct_b64 = msg_obj.get("ciphertextB64")
        tag_b64 = msg_obj.get("tagB64")

        if not (enc_key_b64 and nonce_b64 and ct_b64 and tag_b64):
            raise Exception("Missing encryption fields in message object")

        # Base64 decode
        encrypted_aes_key = base64.b64decode(enc_key_b64)
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ct_b64)
        tag = base64.b64decode(tag_b64)

        # RSA decrypt AES key
        priv = RSA.import_key(self.private_key)
        rsa_cipher = PKCS1_OAEP.new(priv)
        aes_key = rsa_cipher.decrypt(encrypted_aes_key)

        # AES-GCM decrypt
        aes_cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext_bytes = aes_cipher.decrypt_and_verify(ciphertext, tag)

        # Decide what to return based on message type
        msg_type = msg_obj.get("type", "text").lower()

        if msg_type == "file":
            # Return raw bytes for file content
            return plaintext_bytes
        else:
            # Try to decode as text
            try:
                return plaintext_bytes.decode("utf-8")
            except UnicodeDecodeError:
                # In case message isn't proper UTF-8
                return plaintext_bytes.decode("latin-1", errors="replace")

    except Exception as e:
        print("Decryption error:", e)
        return f"Message decryption failed: {e}"
