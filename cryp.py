from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

KEY = 'MySecretKey'
IV = 'MyInitialVector'


def encrypt(plain_str): # 문자열 들어옴
    data = pad(plain_str.encode('utf-8'), AES.block_size) # 문자열 -> 바이트변환후, block_size로 제로패딩 길이가 16배수
    key = pad(KEY.encode('utf-8'), AES.block_size) # 마찬가지
    iv = pad(IV.encode('utf-8'), AES.block_size) # 마찬가지

    cipher = AES.new(key, AES.MODE_CBC, iv=iv) # 객체 생성
    enc = cipher.encrypt(data) # 16배수길이의 바이트문자열을 암호화
    enc_str = b64encode(enc).decode('utf-8') # base 64로 인코드 후 바이트-> 문자열
    return enc_str

def decrypt(enc_str):
    enc = b64decode(enc_str) # base 64로 디코드
    key = pad(KEY.encode('utf-8'), AES.block_size) # 문자열 -> 바이트변환후 제로패딩 16배수로
    iv = pad(IV.encode('utf-8'), AES.block_size) # 문자열 -> 바이트변환후 제로패딩 16배수로

    cipher = AES.new(key, AES.MODE_CBC, iv=iv, ) # 객체 생성
    dec = cipher.decrypt(enc) # 복호화
    dec_str = unpad(dec, AES.block_size).decode('utf-8') # 제로패딩 해제하고 바이트->문자열
    return dec_str

def hash(plain_str):
    data = plain_str.encode('utf-8')
    sha = SHA256.new(data=data)
    h = sha.digest()
    h_str = b64encode(h).decode('utf-8')
    return h_str

def get_random_str():
    # r = get_random_bytes(16)
    # r_str = b64encode(r).decode('utf-8')
    # return r_str
    r = get_random_bytes(8)
    r_str = str(int.from_bytes(r, byteorder="big"))
    return r_str


import sys

if __name__ == '__main__':
    mode = sys.argv[1]
    s = sys.argv[2]
    if mode == '-enc':
        print(encrypt(s), end='')
    elif mode == '-dec':
        print(decrypt(s), end='')
    elif mode == '-hash':
        print(hash(s), end='')
    else:
        print(get_random_str(), end='')
        
    
