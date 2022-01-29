from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode

KEY = 'MySecretKey'
IV = 'MyInitialVector'

def encrypt(plain_str):
    data = pad(plain_str.encode('utf-8'), AES.block_size)
    key = pad(KEY.encode('utf-8'), AES.block_size)
    iv = pad(IV.encode('utf-8'), AES.block_size)

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    enc = cipher.encrypt(data)
    enc_str = b64encode(enc).decode('utf-8')
    return enc_str

def decrypt(enc_str):
    enc = b64decode(enc_str)
    key = pad(KEY.encode('utf-8'), AES.block_size)
    iv = pad(IV.encode('utf-8'), AES.block_size)

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    dec = cipher.decrypt(enc)
    dec_str = unpad(dec, AES.block_size).decode('utf-8')
    return dec_str

def hash(plain_str):
    data = plain_str.encode('utf-8')
    sha = SHA256.new(data=data)
    h = sha.digest()
    h_str = b64encode(h).decode('utf-8')
    return h_str