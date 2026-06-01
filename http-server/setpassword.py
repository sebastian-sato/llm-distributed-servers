import hashlib

password = input("Set password: ")
with open("PASSWORD-SALT.txt", "w+") as f:
    f.write(hashlib.sha256(encode(password)).hexdigest())