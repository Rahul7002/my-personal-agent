from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

# Password hasher supporting both Argon2 (modern standard) and Bcrypt
password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against the stored hash."""
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates a secure salt-and-hash string for a plaintext password."""
    return password_hash.hash(password)