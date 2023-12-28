#!/usr/bin/env python3

from fastapi import HTTPException, Security, Header, Security, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from configparser import ConfigParser

async def get_api_key(api_key: str = Security(Header(None))):
    """Autentificación de la API Key"""
    expected_api_key = "948373984739874" 
    if api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

api_key_header = APIKeyHeader(name="api-key")
config = ConfigParser()
config.read("conf.ini")
api_keys = [config.get('DEFAULT','apikey')]

def get_api_key_(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in api_keys:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


# Oauth2 autentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
