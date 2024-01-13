#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, status, Response, BackgroundTasks, Header, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm, APIKeyHeader
# from fastapi_sessions.session_verifier import SessionVerifier
from starlette.websockets import WebSocketDisconnect
from app import schemas, dependencies, email_sender, email_estructure, datasets_manager, documentation_others, security, google_sheet_imp
from app.security import aes_encrypter, make_backup_s3 # Encrypter and backup maker
from app.redis_database import r,  get_range_name # Redis storage
from fastapi_redis_session import deleteSession, getSession, getSessionId, getSessionStorage, setSession, SessionStorage
from typing import Optional, Annotated, Any
from configparser import ConfigParser
import os, datetime, aiofiles, json, string
import uvicorn
from uuid import uuid4
from uuid import UUID
from pathlib import Path
import google_auth_oauthlib.flow

app = FastAPI(
    title="API Gestión de Prospectos i Comunicaciónes Empresariales",
    summary = "",
    description="\nEstá API diseñada para optimizar la interacción con clientes potenciales y la comunicación empresarial. Funciona recibiendo datos desde una fuente externa, gestionando estos inputs para identificar clientes con potencial. A continuación, automatiza el envío de correos electrónicos a estos clientes, facilitando un seguimiento efectivo. Paralelamente, la API permite a la empresa responder rápidamente sobre el interés en un cliente, verificar la precisión de los datos o actualizar información relevante. Esta interfaz API es una herramienta clave para empresas que buscan mejorar su gestión de relaciones con clientes y optimizar las comunicaciones comerciales.",
    version="0.1",
    docs_url="/docs_00"
)

# Configuración de rutas y directorios y servicios
base_dir = Path(__file__).parent
static_dir = os.path.join(base_dir, 'frontend', 'static')
app.mount("/static", StaticFiles(directory=static_dir), name="static")
os.system('sudo systemctl start internalfeat.service')

# Configuración de plantillas Jinja2 para la interfaz de usuario
templates = Jinja2Templates(directory=base_dir / 'frontend')

# Lectura de la configuración desde archivo INI (incluye host, API key, y puerto)
config = ConfigParser()
config.read(Path("conf.ini"))
host = config['DEFAULT']['host']
api_key = config['DEFAULT']['apikey']
port = config['DEFAULT']['port']

# Instancias de manejo de datos y servicios de email
dataset_manager = datasets_manager.DTManage_manager() # Dataset para gestionar los tokens
email_structure = email_estructure.ClienteEmailFormatter() # Formatear el texto
_email_sender = email_sender.EmailSender("./conf.ini") # Classe para eviar emails 
# aes_encrypter = security.AESEncryptionW_256(Path("app/keys/key_admin.txt")) # Classe para encriptar y desencriptar con AES 256

# Google spreadsheet
google_spreadsheet = google_sheet_imp.Document_CRUD()
google_spreadsheet.Spreadsheet_ID = config['GOOGLE-SHEET']['spreadsheet_id']

# Define cores
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://paumateu.top",
    "http://inutil.top/",
    "http://185.254.206.129/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Luego si quiero puedo especificar los orígenes exactos en la production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------- Gestión de excepciones y Validaciones -------------------------------------

@app.exception_handler(RequestValidationError)
async def vadilation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejar excepciones para RequestValidationError."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )



# ----------------------------- Distintas solicitudes de la API -----------------------------

@app.get("/", description="Función root. Esta función comprueba que la API esté en funcionamiento", tags=["Main"])
def root_conf():
    return RedirectResponse("http://inutil.top/redoc")

# Remove this function in the future :V
@app.get("/docs", tags=["Main"])
def redic_redocs():
    return RedirectResponse("http://inutil.top/redoc")

@app.post("/enviar_cliente", description=documentation_others.enviar_cliente_doc, tags=["Manejo de Clientes"])
async def enviar_client( 
    background_tasks: BackgroundTasks,
    api_key: str = Security(dependencies.get_api_key_),
    *request: schemas.ClientsRequest
):
    mail_structure_dict = []
    client_mana = []

    # Esta parte se encarga de guardar el cliente en un dataset
    for client in request.clientes:
        row_body = {
            'nombre': str(client.nombre),
            'apellidos': str(client.apellidos),
            'numero_telefono': str(client.numero_telefono),
            'codigo_postal': str(client.codigo_postal),
            'url_registro': str(client.url_registro),
            'otra_info': str(datasets_manager.DTManage_manager.dic_writter(dict(client.informacion_adicional))) ,
            'estado':'pendiente',
            'respuesta': "pendiente a responder",
            'campo_adicional': str(client.campo_adicional)
        }
       
        client_mana.append(row_body)
        mail_structure_dict.append(row_body)
    
    # Añadir datos en el google sheet
    values = [list(val.values()) for val in client_mana];range_name = "C19:K10";valueInputOption = "USER_ENTERED"
    background_tasks.add_task(google_spreadsheet.append, range_name, valueInputOption, values)
    
    # Hacer una copia del excel y comprovar datos duplicados
    await update_dataset_from_excel(config['DEFAULT']['apikey'])  

   # Parte que se encarga de estructurar y enviar el correo electronico
    cantidad_clientes, email_estructurado = email_structure.format_email(mail_structure_dict)
    email_subject = f"Tens {int(cantidad_clientes)} {'clients' if int(cantidad_clientes) > 1 else 'client'} {'nous' if int(cantidad_clientes) > 1 else 'nou'} a respondre"

    _email_sender.send_email(receiver_email=config['EMAIL']['email_reciver'], subject=str(email_subject), message_body=email_estructurado)

    if len(client_mana) > 0: 
        return {"status": "success", "response": "Email enviado correctamente"} # "Los clientes han sido recividos, y email enviado correctamente"
    else:
        return {"status": "error", "response":"No has introducido ningún cliente en el cuerpo de la solicitud, mira el cuerpo de la solicitud"}


@app.get("/responder_cliente/", response_class=HTMLResponse, description="Página aparte que te sale para abrir una pestaña aparte para responder la solicitud", tags=["Manejo de Clientes"])
async def client_html_response(request: Request, id: Optional[str] = ''):


    return templates.TemplateResponse("client_camps_verify.html", {'request': request}) # Agregar más campos aquí 


@app.get("/get_json_dataset", description="Este métodoes un metodo que se usaba antes para cargar los datos de los clientes en forma de json.", tags=["Gestor Dataset"])
async def get_json_dataset(api_key: str = Security(dependencies.get_api_key_)):
    json_dataset = dataset_manager.dataset_toJson
    return json_dataset


@app.get("/admin_response", response_class=HTMLResponse, description="Esta es la página del link para que pueda responder la respuesta el admin", tags=["Manejo de Clientes"])
async def admin_accept_response(request: Request, id: Optional[str] = "" , api_key = str(Depends(dependencies.get_api_key))):

    return templates.TemplateResponse('client_verifier_page.html', {"request": request, "variable1": "this is a great variable"})


@app.get("/descargar_tabla", description="Este método es interno, y es usado para mandar al frontend el para descargar la tabla", tags=["Gestor Dataset"])
async def download_table(filename: Optional[str] = "Tabla_clientes.xlsx" , api_key: str = Security(dependencies.get_api_key_)):

    return FileResponse(dataset_manager.get_xlsx_document(filename))


@app.get("/apiconf", response_class=HTMLResponse, description="Pequeño panel html para configurar la API (hacer si me da tiempo)", tags=["Main"])
async def api_conf(request: Request):
    
    # Poner aquí la redirección en vez de en el frontend

    return templates.TemplateResponse(
        'api_conf.html', {
            'request': request, 'apikey':api_key, 'email_sender': config['EMAIL']['email_sender'], 'host':host, 'port': port,'app_password':config['EMAIL']['app_password'],
            'email_reciver':config['EMAIL']['email_reciver'], 'max_columnas_frontend': config['OTROS']['max_columnas_frontend'], 'nombre_columna_reservada': config['OTROS']['nombre_columna_reservada'],
            'username': config['API-OAUTH2']['username'], 'password': config['API-OAUTH2']['password'], 'spreadsheetID': config['GOOGLE-SHEET']['spreadsheet_id']
            }
        )

@app.post("/login", tags=["Sessions"])
async def login(request_body:schemas.UserBody ,api_key = str(Depends(dependencies.get_api_key))):
    # Autenticate user


    # Autenticate useer and password:
    authenticated_user = await check_username(request_body)
    if authenticated_user['status'] == 'failed':
        return {"status":"failed", "message": authenticated_user['message']}


    # session_boddy = schemas.SessionBoddy(
    #     session_id=uuid4(),
    #     username=request_body.username
    # )
    # session_response = await set(session_boddy=session_boddy)

    return {"status":"sucsess","message": "Session has been created succesfuluy"}

@app.post("/get-session", description="Obtener la session actual", tags=["Sessions"])
async def get(session: Any = Depends(getSession)):
    return session


@app.post("/set-session", description="Crear una nueva session", tags=["Sessions"])
async def set(request: Request, response: Response, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    sessionData = await request.json()
    sessionId = setSession(response, sessionData, sessionStorage)
    
    response.set_cookie(key="session_id", value=sessionId, httponly=True, secure=False, samesite='Lax')
    return {"session": f"{sessionData}", "message":f"session has been created succesfully", "session_id":sessionId}


@app.delete("/expire-session", description="Expire the current session in the redis storage and frontend", tags=["Sessions"])
async def expire_session(sessionId: str = Depends(getSessionId), sessionStorage: SessionStorage = Depends(getSessionStorage)):
    deleteSession(sessionId, sessionStorage)
    return None

@app.get("/api_conf_login", response_class=HTMLResponse, description="Verificacion del usuario para acceder a la apiconf", tags=["Main"])
async def api_conf_login(request: Request, redirect: Optional[str] = None):
    
    return templates.TemplateResponse('client_verify.html', {'request': request, 'redirect':redirect})

@app.post("/check_username", description="Método interno para verificar si el usuario es correcto y existe", tags=["Main"])
async def check_username(body_request: schemas.UserBody, api_key=str(Depends(dependencies.get_api_key))):

    # if isinstance(api_key, dependencies.get_api_key):
    #     return HTTPException(404, detail="You haven't provided any apikey")
    
    # Check if user exists or if is diabled
    user = security.get_user_db(security.fake_users_db2, body_request.username)
    if not user:
        return {"status":"failed", "message": f"User \"{body_request.username}\" doesn't exists"}
    if user.disabled:
        return {"status":"failed", "message": f"Uses \"{body_request.username}\" is diabled"}

    # Check if password is correct
    if  user.password.decode('utf-8')  != body_request.password:
        return {"status":"failed", "message": "Incorrect password"}


    return {"status":"succes", "message": f"User {body_request.username} is avariable","apikey_provided": api_key}

@app.patch("/update_dataset_", description=r"Método interno para leer el excel y actualizar el dataset del servidor\n*header* -> {'api-key':string}", tags=["Gestor Dataset"])
async def update_dataset_from_excel(background_tasks: BackgroundTasks, api_key: str = Security(dependencies.get_api_key_)):

    range_name = dataset_manager.get_excel_range
    
    all_new_values = google_spreadsheet.read_excel(str(range_name), enum=True)
    await dataset_manager.update_dataset_status(all_new_values)

    return {"status":"success", "message":"Dataset updated", "values":range_name}

@app.patch("/update_columns_", description=r"Método interno que se encarga de leer los nombres de las columnas del exce, el estado y actualizar (si es necesario), el archivo de configuración en caso de haber cambios", tags=["Gestor Dataset"])
async def update_num_status_col(api_key: str = Security(dependencies.get_api_key_)):
    column_configuration = google_spreadsheet.get_all_columns_name_and_status()

    def int_to_letter(number):
        if 1 <= number <= 26:
            # Subtracting 1 because indices start at 0
            return string.ascii_uppercase[number - 1]
        else:
            return "Z"

    range_name = {
        'range_name': f'C9:{int_to_letter(len(column_configuration) + 2)}99999999'
    }

    async with aiofiles.open(Path('app/config/config_column_status.json'),'w') as f:
        await f.write(json.dumps(column_configuration, indent=4))

    async with aiofiles.open(Path('app/config/general_config.json'), 'w') as f:
        await f.write(json.dumps(range_name, indent=4))      

    return {"status":"success", "message": "Information updated successfully"}


@app.post("/make_backup", description="Make a backup of the dataset and send to S3 (AWS)", tags=["Gestor Dataset"])
async def make_backup(background_tasks: BackgroundTasks, api_key: str = Security(dependencies.get_api_key_)):
    try:
        # The task is added as a backround task
        background_tasks.add_task(make_backup_s3)
        return {"message":f"Backup completed sucessfully"}
    except Exception as e:
        return {"error":f"An error ocurred: {e}"}


"""
@app.post("/api_set_conf", description="Metodo interno para aplicar la configuración")
async def set_api_cong(request: schemas.ApiConf, api_key=str(Depends(dependencies.get_api_key))):
    # Aplicar OAUTH2 al acceder a esta función! importantísimo


    # Vadilar si los datos sean correctos ? 
    

   
    if True:  # ? true aplicar cambios : false lanzar error diciendo que los cambios son incorrectos
        config['DEFAULT']['apikey'] = request.apikey
        config['DEFAULT']['host'] = request.host
        config['DEFAULT']['port'] = request.port
        
        config['EMAIL']['email_sender'] = request.email_sender
        config['EMAIL']['app_password'] = request.app_password
        config['EMAIL']['email_reciver'] = request.email_reciver

        config['OTROS']['max_columnas_frontend'] = request.max_columns_frontend
        config['OTROS']['nombre_columna_reservada'] = request.name_reserved_column

        config['API-OAUTH2']['username'] = request.username
        config['API-OAUTH2']['password'] = request.password

        config['GOOGLE-SHEET']['spreadsheed_id'] = request.spreadsheetID

        # Actualizar registros
        with open(Path('conf.ini'), 'w') as configfile:
            config.write(configfile)

    return JSONResponse({'status':'succes','response':'La nueva configuración ha sido cambiada correctamente'})
"""
# ------------ WebSockets endpoinds -----------------------------------------------

@app.websocket("/ws_tabla")
async def webdocket_endpoint(websocket: WebSocket):
    """Websocket para enviar los datos a la tabla"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Handle the received messages...
            # If 'get_data' is received, send the JSON data back to the client
            if data == 'get_data':
                json_data = dataset_manager.dataset_toJson
                await websocket.send_text(json_data)
    except WebSocketDisconnect as e:
        # Handle the disconnect event, log it or clean up resources
        print(f"Client disconnected with code: {e.code}")


# ------------------- OAuth Autentication ----------------------------------------------------------------

@app.get("/code", description="Redirect URI for API authentication", tags=["Pendiente a implementar"])
async def redirect_uri(request: Request):
 # Extract the authorization code from the request
    code = request.query_params.get('code')

    if code:
        # Create the flow using the client secret file and the same scopes as before
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets'],
            redirect_uri='https://www.example.com/code')  # Your actual redirect URI

        # Fetch the token using the code
        flow.fetch_token(code=code)

        # Here you can save the credentials for later use
        credentials = flow.credentials
        # You can save these credentials or use them directly to access Google APIs

        # Redirect or respond as necessary
        return {"message": "Authentication successful"}

    else:
        # Handle the case where there is no code in the query string
        return {"error": "No authorization code provided"}


async def get_current_user(token: str = Depends(dependencies.oauth2_scheme)):
    """This function is designed to decode a token and return the corresponding user"""
    user_dict = security.decode_token(token)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={'WWW-Authenticate': 'bearer'},
        )
    user = security.get_user_db(security.fake_users_db2, user_dict['sub'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return user
    

async def get_current_active_user(
        current_user: Annotated[security.User, Depends(get_current_user)]
):
    """get the active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# @app.post("/token", description="Token endpoint for user authentication")
# async def token_create(from_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
#     user = security.get_user_db(security.fake_users_db2, from_data.username)

#     if not user:
#         raise HTTPException(status_code=400, detail=f"Incorrect username or password")
    
#     user_val = await check_username(from_data)
#     if user_val['status'] == 'failed':
#         raise HTTPException(status_code=400, detail=user_val['message'])
    
#     # Generate a token (to be replaced with a real JWT or similar token)
#     token = security.create_acces_token(data={"sub":user.username}, expire_delta=datetime.timedelta(days=30)) # At this moment, the token will expires in 30 days

#     return {"acces_token": token, "token_type": "bearer"}
 

# @app.get("/users/me", description="add description here abot what this functiondoes")
# async def read_ysers_me(
#     current_user: Annotated[security.User, Depends(get_current_active_user)]
# ):
#     return current_user



if __name__ == "__main__":
    # uvicorn main:app --host 0.0.0.0 --port 443
    
    # search process -> sudo lsof -i :80 | 443
    uvicorn.run(
        "main:app",
        host = host, 
        port = int(port),
        ssl_keyfile = None,
        log_level = "debug",
        reload=True
    )