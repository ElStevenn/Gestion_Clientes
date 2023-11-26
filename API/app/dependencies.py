#!/usr/bin/env python3

from fastapi import HTTPException, Security, Header
from fastapi.security import OAuth2PasswordBearer# Use this to oauth2

async def get_api_key(api_key: str = Security(Header(None))):
    """Autentificación de la API Key"""
    expected_api_key = "948373984739874" # Then, change this to an apiKey
    if api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# Oauth2 autentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
