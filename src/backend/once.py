from cryptography.fernet import Fernet

# generate a master key for encrypting the provider api keys
key = Fernet.generate_key()
# save to .env
with open(".env", "a") as f:
    f.write(f"MASTER_KEY={key.decode()}\n")

# generate a secret key for signing the jwt tokens
key = Fernet.generate_key()
# save to .env
with open(".env", "a") as f:
    f.write(f"SECRET_KEY={key.decode()}\n")
