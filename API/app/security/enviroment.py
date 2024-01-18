
from typing import Any
from pathlib import Path
from passlib.context import CryptContext
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from hashlib import sha256
import os, base64, json
"""
This class is responbile to save the KEYS save

"""

class AESEncryptionW_256:
    """
    
    Encrption  class with Advanced Encryption Standard with 256 bits, created by Pau Mateu
    -----------------------
    Encrypt:    

    

    """
    def __init__(self):
        string_key = "Your_String_Key_Here"
        self.key = sha256(string_key.encode()).digest()

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



class Enviroment_variable:
    """
    Class used to create environment variables and encrypt them.
    """
    KEY_PATH = Path("/home/ubuntu/certificates/secure_data")  # Change this as needed

    def __init__(self):
        self.aes = AESEncryptionW_256()

    def get_hash_name(self, input_string: str):
        """To hash the variable name (not the value)"""
        return sha256(input_string.encode()).hexdigest()      

    def __setitem__(self, __key, __value): 
        encrypted_variable = self.aes.encrypt(__value)
        if encrypted_variable is None:
            raise Exception("Encryption failed, returned None")

        encrypted_variable_b64 = base64.b64encode(encrypted_variable).decode('utf-8')
        hashed_key = self.get_hash_name(__key)

        try:
            with open(self.KEY_PATH / 'environ_variables.json', 'r') as f:
                file_content = f.read()
                if not file_content:  # Check if the file is empty
                    all_data = {}
                else:
                    all_data = json.loads(file_content)
        except (FileNotFoundError, json.JSONDecodeError):
            all_data = {}

        all_data[hashed_key] = encrypted_variable_b64

        with open(self.KEY_PATH / 'environ_variables.json', 'w') as f:
            json.dump(all_data, f, indent=4)



    def __getitem__(self, key):
        if key in ["aes", "get_hash_name", "KEY_PATH"]:
            return object.__getattribute__(self, key)

        hashed_key = self.get_hash_name(key)
        try:
            with open(self.KEY_PATH / 'environ_variables.json', 'r') as f:
                all_data = json.load(f)
            
            encrypted_variable_b64 = all_data[hashed_key]
            encrypted_variable = base64.b64decode(encrypted_variable_b64)

            return self.aes.decrypt(encrypted_variable).decode()
        except (FileNotFoundError, KeyError, json.JSONDecodeError, ValueError):
            return None


    def __delitem__(self, key):
        try:
            with open(self.KEY_PATH / 'environ_variables.json', 'r') as f:
                all_data = json.load(f)

            hashed_key = self.get_hash_name(key)
            del all_data[hashed_key]

            with open(self.KEY_PATH / 'environ_variables.json', 'w') as f:
                json.dump(all_data, f, indent=4)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass



if __name__ == "__main__":
    env_variable = Enviroment_variable()
    env_variable["SECRET_KEY"] = "a548807d-8197-4431-b11b-10d0d5af66d1"
    print(env_variable["SECRET_KEY"])