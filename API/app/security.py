#!/usr/bin/env python3

import os, boto3, random
from jwt import decode, PyJWTError, encode, ExpiredSignatureError, InvalidTokenError
import datetime, re
from typing import Any, Dict
from pydantic import BaseModel
from struct import pack
from passlib.context import CryptContext
from pathlib import Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from base64 import b64encode, b64decode
from .db_connection.crud import get_user
from .db_connection import schemas, models
from .db_connection.database import async_engine, AsyncSession
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import hashlib,asyncio
from boto3.dynamodb.conditions import Key

"""
 Security classes.

  - What is AES 256?
     Advanced Encryption Standard (AES) 256 is a virtually impenetrable symmetric encryption algorithm 
     that uses a 256-bit key to convert your plain text or data into a cipher.

  - Create session

  - Make Backups to S3 (AWS service)  

  - 

"""


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    password: bytes



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "secret_key"

# IOn the future change this, this is just an improvisation
def fake_hash_password(password: str):
    return "fakehashed" + password

def get_user_db(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def decode_token(coded_token: str):
    try:
        decoded_token = decode(coded_token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except ExpiredSignatureError:
        # If token expired means that the user has to login again
        return "Token expired"
    except InvalidTokenError:
        return "Invalid token"

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

def create_access_token(data: Dict[str, Any], expire_delta: datetime.timedelta = None):
    """
    Create an access token for the given user data.

    Args:
    - data (Dict[str, Any]): The data to encode in the token, typically user identity.
    - expire_delta (datetime.timedelta, optional): The amount of time for the token to expire.

    Returns:
    - str: The generated JWT token as a string.
    """
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.datetime.utcnow() + expire_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt





class AESEncryptionW_256:
    """
    
    Encrption  class with Advanced Encryption Standard with 256 bits, created by Pau Mateu
    -----------------------
    Encrypt:    

    

    """
    def __init__(self):
        self.key = os.environ.get("KEY_AES")

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

async def autenticate_user(username: str, password: str):
    try:
        async with AsyncSession(async_engine) as db:
            return await check_session(db, username, password)
    
    except ValueError:
        return False



class AES_256_encrypter:
    def __init__(self):
        pass
    
    def encrypt(self, plaintext, password: str):
        # generate a random salt 
        salt = get_random_bytes(AES.block_size)

        # use the Scrypt KDF to get a private key from the password
        private_key = hashlib.scrypt(
            password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

        # create cipher config
        cipher_config = AES.new(private_key, AES.MODE_GCM)

        # return a dictionary with the encrypted text
        cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plaintext, 'utf-8'))
        return (
             cipher_text, # Encrypted text
             salt,  # Salt
             cipher_config.nonce,  # Nonce
             tag # Tag
        )


    def decypt(self, enc_dict: dict, provided_password: str):
        try:
            # decode the dictionary entries from base64
            salt = b64decode(enc_dict['salt'])
            cipher_text = b64decode(enc_dict['cipher_text'])
            nonce = b64decode(enc_dict['nonce'])
            tag = b64decode(enc_dict['tag'])

            # generate theprivate key from the password and salt
            private_key = hashlib.scrypt(
            provided_password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

            # create the cipher config
            cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)

            # decypt the cipher text
            decrypted = cipher.decrypt_and_verify(cipher_text, tag)
            return decrypted
        except (ValueError, KeyError):
            # The password provided is worng
            return None
encrypter_AES256 = AES_256_encrypter()

async def create_user(db: AsyncSession, user_request: schemas.CreateUser):
    # Encrypt password and save the user
    cipher_text, salt, nonce, tag = encrypter_AES256.encrypt(user_request.username, user_request.password)

    try:
        async with db.begin():
            # Create a new user
            new_user = models.Authorized_users(
                username=user_request.username,
                email=user_request.email,
                ecipher_text=cipher_text,
                role_=user_request.role_,
                salt=salt,
                nonce=nonce,
                tag=tag
            )
            db.add(new_user)
            
        # Query all users
        async with db.begin():
            await db.execute(select(models.Authorized_users))
            return {"result":"success", "message": f"User {new_user.username} with email {new_user.email} has been created"}
        
    except IntegrityError as e:
        error_info = str(e.__dict__['orig'])
        duplicate_field = re.search(r'\((.*?)\)=', error_info)
        if duplicate_field:
            field_name = duplicate_field.group(1)
            return {"result": "error", "message": f"\"{field_name}\" is already taken into the database"}
        else:
            return {"result": "error", "message": "An unknown integrity error occurred."}

async def check_session(db: AsyncSession, username: str, provided_password: str):
    # Check if username and password are correct
    # Get username
    user_data = await get_user(db, username)

    username = user_data[1]
    enc_dict = {
    'cipher_text': b64encode(user_data[3]).decode('utf-8'),
    'salt': b64encode(user_data[5]).decode('utf-8'),
    'nonce': b64encode(user_data[6]).decode('utf-8'),
    'tag': b64encode(user_data[7]).decode('utf-8')
    }

    # Decrypt password and check if password is corret
    decrypted_password = encrypter_AES256.decypt(enc_dict, provided_password)
    try:
        if bytes.decode(decrypted_password) == username:
            # Session provided correct
            return (True, user_data[4])

    except ValueError:
        raise ValueError("Password provided is wrong")




if __name__ == "__main__":
    # import os
    # from dotenv import load_dotenv
    # load_dotenv()
    # print(os.getenv("KEY_W"))
    
    

    '''paus_password = "mierda69"
    password_owner = "Pau_Mateu"

    cipher_text, salt, nonce, tag = encript_256.encrypt(paus_password, paus_password)
    enc_dict = {
        'cipher_text': b64encode(cipher_text).decode('utf-8'),
        'salt': b64encode(salt).decode('utf-8'),
        'nonce': b64encode(nonce).decode('utf-8'),
        'tag': b64encode(tag).decode('utf-8')
    }
    print(enc_dict)

    provided_password = "pollo"
    decrypted_password = encript_256.decypt(enc_dict, provided_password)
    print(bytes.decode(decrypted_password))
    '''