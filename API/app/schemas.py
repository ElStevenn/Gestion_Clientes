#!/usr/bin/env python3

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List,  ClassVar
from configparser import ConfigParser
from pathlib import Path
import aiofiles, json, asyncio
from uuid import UUID

async def read_schema_values():
    async with aiofiles.open(Path('config/config_column_status.json'), 'r') as f:
        content = await f.read()
        values = json.loads(content)

    return [val.get('value', None) for val in values]

class ClientBaseData(BaseModel):

    nombre: str
    apellidos: str
    numero_telefono: str
    codigo_postal: str
    url_registro: str
    campo_adicional: Optional[str] = ""
    informacion_adicional: Optional[Dict[str, str]] = Field(default={})
    informacion_adicional_str: Optional[str] = None

    # Elimina la lógica de transformación de este validador
    @validator('informacion_adicional', pre=True, allow_reuse=True)
    def validate_informacion_adicional(cls, v):
        if not isinstance(v, dict):
            raise ValueError("La información adicional debe ser un diccionario.")
        return v

class ClientsRequest(BaseModel):
    clientes: List[ClientBaseData]

class ClientResponse(BaseModel):
    client_id:  str 
    response: str
    comments: Optional[str] = None

class ApiConf(BaseModel):
    config: ClassVar[ConfigParser] = ConfigParser()
    config.read(Path("conf.ini"))

    apikey: Optional[str] = config.get('DEFAULT', 'apikey', fallback=None)
    host: Optional[str] = config.get('DEFAULT', 'host', fallback=None)
    port: Optional[str] = config.get('DEFAULT', 'port', fallback=None)

    email_sender: Optional[str] = config.get('EMAIL', 'email_sender', fallback=None)
    app_password: Optional[str] = config.get('EMAIL', 'app_password', fallback=None)
    email_reciver: Optional[str] = config.get('EMAIL', 'email_reciver', fallback=None) 

    max_columns_frontend: Optional[str] = config.get('OTROS', 'max_columnas_frontend', fallback=None)
    name_reserved_column: Optional[str] = config.get('OTROS', 'nombre_columna_reservada', fallback=None)

    # auth2
    username: Optional[str] = config.get('API-OAUTH2', 'username', fallback=None)
    password: Optional[str] = config.get('API-OAUTH2', 'password', fallback=None)

    spreadsheetID: Optional[str] = config.get('GOOGLE-SHEET','spreadsheet_id', fallback=False)


class UsernameBasic(BaseModel):
    username: str

class UserBody(UsernameBasic):
    password: str


class SessionBoddy(UsernameBasic):
    session_id: UUID

class SessionData(BaseModel):
    # Data in the server's memory
    username: str
    token: str = None


class UserLoginBasicBody(SessionData): 
    password: str # None encrypted password through this shema



async def main():
    values = await read_schema_values()
    print(values)

if __name__ == "__main__":
    asyncio.run(main())
