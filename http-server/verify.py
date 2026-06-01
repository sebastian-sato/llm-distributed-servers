import hashlib

def verify_password(password):
    with open("./PASSWORD-SALT.txt", 'r') as f:
        password_salt = f.read().split('\n')[0].strip()
    if hashlib.sha256(password.encode()).hexdigest() == password_salt:
        return True
    return False
