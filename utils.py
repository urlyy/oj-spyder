from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import secrets

import yaml

with open('config.yaml', 'r') as file:
    data = yaml.safe_load(file)
    encryptor = data.get('encryptor')

# 长128位
key = eval("b'"+encryptor['key']+"'")
iv = eval("b'"+encryptor['iv']+"'")
backend = default_backend()
cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
encryptor = cipher.encryptor()
decryptor = cipher.decryptor()

def random_bytes(bit=8)-> bytes:
    return secrets.token_hex(bit).encode()

# 加密
def encrypt(plaintext:str)-> str:
    b = plaintext.encode()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(b) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return str(ciphertext)[2:-1]

# 解密
def decrypt(ciphertext:str)->str:
    ciphertext = eval("b'"+ciphertext+"'")
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return unpadded_data.decode()


def testEncrypt(pwd):
    bs = encrypt(pwd)
    with open('pwd.txt','w') as f:
        f.write(bs)

def testDecrypt():
    with open("./pwd.txt", "r") as f:
        bs = f.read()
    print(decrypt(bs))
    
testEncrypt("qwer")
testDecrypt()


