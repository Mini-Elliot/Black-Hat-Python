from Crypto.PublicKey import RSA

# Generate a new RSA key pair
new_key = RSA.generate(2048, e=65537)

# Export the public and private keys in PEM format
public_key = new_key.publickey().export_key("PEM")
private_key = new_key.export_key("PEM")

# Print the keys as decoded strings
print(public_key.decode())
print(private_key.decode())
