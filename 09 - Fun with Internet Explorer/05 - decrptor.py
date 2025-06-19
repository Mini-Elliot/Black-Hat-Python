import zlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Paste your private key here as a multiline string
private_key = """
-----BEGIN RSA PRIVATE KEY-----
...your private key here...
-----END RSA PRIVATE KEY-----
"""

# Paste the encrypted Base64-encoded string here
encrypted_b64 = "###PASTE BASE64 ENCRYPTED PAYLOAD HERE###"

# Import private key and initialize decryptor
rsakey = RSA.import_key(private_key)
cipher = PKCS1_OAEP.new(rsakey)

# Decode base64-encoded ciphertext
encrypted_data = base64.b64decode(encrypted_b64)

# Decrypt in chunks
chunk_size = 256
offset = 0
decrypted = b""

while offset < len(encrypted_data):
    chunk = encrypted_data[offset:offset + chunk_size]
    decrypted += cipher.decrypt(chunk)
    offset += chunk_size

# Decompress to retrieve original plaintext
plaintext = zlib.decompress(decrypted)

# Print as UTF-8 decoded string
print(plaintext.decode('utf-8'))
