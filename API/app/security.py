#!/usr/bin/env python3

import os, re, boto3, random
from jwt import decode, PyJWTError, encode
import datetime
from typing import Any, Dict
from pydantic import BaseModel
from struct import pack
from passlib.context import CryptContext
from pathlib import Path

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import asyncio
from boto3.dynamodb.conditions import Key

class AESEncryptionW_256:
    """
    
    Encrption  class with Advanced Encryption Standard with 256 bits, created by Pau Mateu
    -----------------------
    Encrypt:
    

    

    """
    def __init__(self, key_path):

        # The key has to be stored into a file
        self.key =  open(key_path, 'rb').read()

    def pad(self, data):
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    def unpad(self, padded_data):
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data

    def encrypt(self, data):
        iv = os.urandom(16)
        padded_data = self.pad(data.encode())
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted_data

    def decrypt(self, encrypted_data):
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return self.unpad(padded_data)

aes_encrypter = AESEncryptionW_256(Path('app/keys/key_admin.txt'))

# Admin role is the unique user who can create users
fake_users_db2 = {
    "admin_":{
        "id":"fb81a29c-60b1-4f51-80d2-56b722b9119d",
        "username":"admin_",
        "full_name":"Pau Mateu Esteve",
        "email":"paumat17@gmail.com",

        "password": aes_encrypter.decrypt(open(Path('app/keys/admin_password.txt'), 'rb').read()),
        "hashed_password": base64.b64encode(open(Path('app/keys/admin_password.txt'), 'rb').read()),

        "role":"admin",
        "tokens":[],
        "disabled": False
    },
    "invited": {
        "id":"6d92b43f-8c18-4b63-ae32-e9e4871da22e",
        "username":"invited",
        "full_name":"Federico García Olca",
        "email":"federicogarcía@gmail.com",
        "password": aes_encrypter.decrypt(open(Path('app/keys/password_invited.txt'), 'rb').read()),
        "hashed_password":base64.b64encode(open(Path('app/keys/password_invited.txt'), 'rb').read()),

        "role":"user",
        "tokens":[],
        "disabled": False
    },
    "federico": {
        "id":"a19403ec-19a4-46ce-8d40-31f891420735",
        "username":"federico",
        "full_name":"Federico García Parra",
        "email":"federicaparra@gmail.com",

        "password": aes_encrypter.decrypt(open(Path('app/keys/password_federico.txt'), 'rb').read()),
        "hashed_password": base64.b64encode(open(Path('app/keys/password_federico.txt'), 'rb').read()),

        "role": "contributor",
        "tokens": [],
        "disabled": True
    },
    "paula": {
        "id":"e5462504-f765-4ca5-97b5-4b41296fc36b",
        "username":"paula",
        "full_name":"Paula Gómez Vonespié",
        "email":"paulera123@gmail.com",

        "password": aes_encrypter.decrypt(open(Path('app/keys/password_paula.txt'), 'rb').read()),
        "hashed_password": base64.b64encode(open(Path('app/keys/password_paula.txt'), 'rb').read()),

        "role":"user",
        "tokens": [],
        "disabled": False
    },
    "susano":{
        "id":"2e3de1ae-f9a7-42d8-a892-8591de7821d1",
        "username":"susano",
        "full_name":"Susano Garría Olona",
        "email":"susanerista@gmailo.com",

        "password": aes_encrypter.decrypt(open(Path('app/keys/password_susano.txt'), 'rb').read()),
        "hashed_password": base64.b64encode(open(Path('app/keys/password_susano.txt'), 'rb').read()),
        "role":"user",
        "tokens": [],
        "disabled": False
    }
}


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    password: bytes



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "secret_key" # change this to os variable

# IOn the future change this, this is just an improvisation
def fake_hash_password(password: str):
    return "fakehashed" + password

def get_user_db(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def decode_token(token: str):
    try:
        decoded_token = decode(jwt=token, key=SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except PyJWTError as e:
        # Here you could log the exception or handle it as needed
        raise e

def authenticate_user(db, username: str, password):
    user = get_user_db(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def verify_password(plain_password: str, hashed_password: str):
    decoded_token = decode_token(hashed_password)
    if decoded_token['password'] == plain_password:
        return True
    else:
        return False



def get_password_hash(password):
    return pwd_context.hash(password)

def create_acces_token(data: Dict[str, Any], expire_delta: datetime.timedelta = None):
    """
    Create an access token for the given user data.

    Args:
    - data (Dict[str, Any]): The data to encode in the token, typically user identity.
    - expires_delta (datetime.timedelta, optional): The amount of time for the token to expire.

    Returns:
    - str: The generated JWT token as a string.
    """
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.datetime.utcnow() + expire_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt







class AESEncryptionW_256:
    """
    
    Encrption  class with Advanced Encryption Standard with 256 bits, created by Pau Mateu
    -----------------------
    Encrypt:
    

    

    """
    def __init__(self, key):
        self.key = key

    def pad(self, data):
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    def unpad(self, padded_data):
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data

    def encrypt(self, data):
        iv = os.urandom(16)
        padded_data = self.pad(data.encode())
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted_data

    def decrypt(self, encrypted_data):
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return self.unpad(padded_data)
        

def make_backup_s3():
    """
    Function to make backups into an S3 Bucket. Designed to store CSV files as security copies.
    Utilizes S3 for its reliability and ease of use.
    """

    # Environment variables for AWS credentials and region
    access_key = os.environ.get('ACCES_KEY')
    secret_access_key = os.environ.get('SECRET_ACCES_KEY')
    region_name = "us-east-1"

    # Create S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=region_name
    )

    # S3 bucket name
    bucket_name = 'paus-private-storage'

    # File path to upload and target file name in S3
    file_to_upload = Path('datasets/main_dataset_manager2.csv')
    date = datetime.datetime.now()
    target_key = f'cliente_gestor_backups/tabla_users_{date.day}-{date.month}-{date.year}.csv'

    # Upload the file
    s3_client.upload_file(str(file_to_upload), bucket_name, target_key)
    print(f"File uploaded to S3 as {target_key}")
  





if __name__ == "__main__":
    make_backup_s3()


    # Read 256 bites key
    
    """passowrd_provided = "123qweasd"

    federico = get_user_db(fake_users_db2, 'invited')
    # federico_password = federico.hashed_password

    
    print(federico)
    federico_password = federico.password
    print(federico_password.decode('utf-8'))
    # decrypted_password = 
    if federico_password.decode('utf-8') != passowrd_provided:
        print("Password unmatch")
    else:
        print("Password match")

    # Read 32 byted key
    key = open('keys/key_admin.txt', 'rb').read()
    aes_encrypter = AESEncryptionW_256(key)
    

    user = get_user_db(fake_users_db2, "federico")
    print(user)
    """
