#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, status, Response, BackgroundTasks, Header, Security, Cookie, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.openapi.docs import get_swagger_ui_html
# from fastapi_sessions.session_verifier import SessionVerifier
from starlette.websockets import WebSocketDisconnect
from app import schemas, dependencies, email_sender, email_estructure, datasets_manager, documentation_others, security, google_sheet_imp
from app.security.backups import make_backup_s3
from app.security.encryption import autenticate_user, create_access_token, authenticate_token
from app.db_connection import crud
from app.schema_send_client import DynamicModel, client_schema_definition, get_schema_columns
from fastapi_redis_session import deleteSession, getSession, getSessionId, getSessionStorage, setSession, SessionStorage
from typing import Optional, Any, List
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
    version="0.2.1",
    contact={
        "name": "Pau Mateu",
        "url": "https://paumateu.com/",
        "email": "paumat17@gmail.com",
    },
    docs_url=None,
    redoc_url=None
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

# Genera elswagger del /docs
swagger_ui_html_content = get_swagger_ui_html(
    openapi_url="/openapi.json",
    title="API Gestión de Prospectos i Comunicaciónes Empresariales",
    swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
    swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    swagger_favicon_url="http://inutil.top/static/images/icon.png",
    oauth2_redirect_url=None,
    init_oauth=None,
    
    
).body.decode()


# ----------------------------- Gestión de excepciones y Validaciones -------------------------------------

@app.exception_handler(RequestValidationError)
async def vadilation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejar excepciones para RequestValidationError."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

# ----------------------------- Distintas solicitudes de la API -----------------------------

@app.get("/", description="Pantalla de bienvenida para el cliente", include_in_schema=False)
def root_conf(request: Request):
    return templates.TemplateResponse("api_welcome.html", context={'request': request})

# Remove this function in the future ->
@app.get("/docs", tags=["Main"])
async def redic_redocs(request: Request):
    cookies = request.cookies
    try:
        # Autenticate user 
        username, role, id_ = await authenticate_token(cookies['token_beaber'] if cookies['token_beaber'] else None)
    except KeyError:
        return RedirectResponse('http://inutil.top/api_conf_login')
    
    # Vadilate credentials
    result = await crud.vadilate_user_credentials(username, role, id_)

    # Check result status
    if result[1] in ["root", "admin"] :
        return HTMLResponse(content=swagger_ui_html_content, )
        
    elif result[1] == "user":
        return PlainTextResponse("Your user doesn't have the enough privilleges to be here")
    else:
        return RedirectResponse('http://inutil.top/api_conf_login')

    
@app.post("/enviar_cliente", description=documentation_others.enviar_cliente_doc, tags=["Manejo de Clientes"])
async def enviar_client( 
    client_body: DynamicModel,
    background_tasks: BackgroundTasks,
    api_key: str = Security(dependencies.get_api_key_),
   
):

    data_dict = client_body.dict()
    values_list = list(data_dict.values()) # Get all the values in a list

    # Save the model in the dataset 
    # await dataset_manager.add_new_row(*values_list)

    return {"response": values_list, "type": str(type(data_dict))}
    """
        client_mana.append(row_body)
        mail_structure_dict.append(row_body)
    """
    """
        # Añadir datos en el google sheet
        values = [list(val.values()) for val in client_mana];range_name = "C19:K10";valueInputOption = "USER_ENTERED"
        background_tasks.add_task(google_spreadsheet.append, range_name, valueInputOption, values)
        
        # Hacer una copia del excel y comprovar datos duplicados
        await update_dataset_from_excel(config['DEFAULT']['apikey'])  

    # Parte que se encarga de estructurar y enviar el correo electronico
        cantidad_clientes, email_estructurado = email_structure.format_email(mail_structure_dict)
        email_subject = f"Tienes {int(cantidad_clientes)} {'clients' if int(cantidad_clientes) > 1 else 'client'} {'nuevos' if int(cantidad_clientes) > 1 else 'nou'} a responder"

        _email_sender.send_email(receiver_email=config['EMAIL']['email_reciver'], subject=str(email_subject), message_body=email_estructurado)

        if len(client_mana) > 0: 
            return {"status": "success", "response": "Email enviado correctamente"} # "Los clientes han sido recividos, y email enviado correctamente"
        else:
            return {"status": "error", "response":"No has introducido ningún cliente en el cuerpo de la solicitud, mira el cuerpo de la solicitud"}
    """

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


@app.get("/descargar_tabla/{token_beaber}", description="Este método es interno, y es usado para mandar al frontend el para descargar la tabla", tags=["Gestor Dataset"])
async def download_table(token_beaber: str, filename: Optional[str] = "Tabla_clientes.xlsx"):

    return FileResponse(dataset_manager.get_xlsx_document(filename))

@app.put("/update_schema_client", description="Update the sechema definition from a column given", tags=["Manejo de Clientes"])
async def update_schema_client_(background_tasks: BackgroundTasks, api_key: str = Security(dependencies.get_api_key_)):
    background_tasks.add_task(client_schema_definition)

    return {"result":"success", "response":"The schema definiton has been updated"}

@app.get("/apiconf", response_class=HTMLResponse, description="Pequeño panel html para configurar la API (hacer si me da tiempo)", tags=["Main"])
async def api_conf(request: Request):
    # Get cookie to see if thr client has the correct token
    cookies = request.cookies
    if not cookies:
        return RedirectResponse('http://inutil.top/api_conf_login')
    
    # Autenticate user 
    username, role, id_ = await authenticate_token(cookies['token_beaber'])

    # Vadilate credentials
    result = await crud.vadilate_user_credentials(username, role, id_)

    # Check result status
    if result:
        if result[1] == "root":
            # User authenticated
            return templates.TemplateResponse(
                'api_conf.html', {
                    'request': request, 'apikey':api_key, 'email_sender': config['EMAIL']['email_sender'], 'host':host, 'port': port,'app_password':config['EMAIL']['app_password'],
                    'email_reciver':config['EMAIL']['email_reciver'], 'username': config['API-OAUTH2']['username'],
                    'password': config['API-OAUTH2']['password'], 'spreadsheetID': config['GOOGLE-SHEET']['spreadsheet_id']
                    }
                )
        elif result[1] == "admin":
            return PlainTextResponse("Admin doesn't required to be here")
        elif result[1] == "user":
            return PlainTextResponse("Admin doesn't required to be here")
        else:
            return RedirectResponse('http://inutil.top/api_conf_login')
    else:
        return RedirectResponse('http://inutil.top/api_conf_login')


@app.get("/whoami", description="Authenticate token beaber by its cookie", tags=["Sessions"])
async def whoami(token_beaber: str = Cookie('token_beaber')):

    # Autenticate user
    username, role, id_ = await autenticate_user(token_beaber)
    try:
        # Vadiate credentials
        result = await crud.vadilate_user_credentials(username, role, id_)
        if result[1] == "root" or result[1] == "admin" or result[1] == "user":
            return {"status":"success", "role": result[1], "message":"User authorized succsessfully"}
        

    except TypeError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User not authorized",
            headers={'WWW-Authenticate': 'Bearer'}
        )


@app.post("/login", description="", tags=["Sessions"])
async def login(request_body:schemas.UserTokenLogin, api_key: str = Security(dependencies.get_api_key_)):

    # Autenticate user
    username, role, id_ = await authenticate_token(request_body.token_beaber)

    # Vadilate credentials
    result = await crud.vadilate_user_credentials(username, role, id_)

    if result:
        if result[1] == "root":
            # Change this in the furure, i think is worng
            return {"status":"success","message":"user authorized as root", "role": result[1]}
        
        

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="user not authorized",
            headers={'WWW-Authenticate': 'Bearer'}
        )
    

@app.delete("/expire-session", description="Metodo pendiente de hacer para expirar la sessión", tags=["Sessions"], deprecated=True)
async def expire_session(sessionId: str = Depends(getSessionId), sessionStorage: SessionStorage = Depends(getSessionStorage)):
    deleteSession(sessionId, sessionStorage)
    return None

@app.get("/api_conf_login", response_class=HTMLResponse, description="Verificacion del usuario para acceder a la apiconf", tags=["Main"])
async def api_conf_login(request: Request, redirect: Optional[str] = None):
    
    return templates.TemplateResponse('client_verify.html', {'request': request, 'redirect':redirect})


@app.patch("/update_dataset_", description=r"Método interno para leer el excel y actualizar el dataset del servidor\n*header* -> {'api-key':string}", tags=["Gestor Dataset"], include_in_schema=False)
async def update_dataset_from_excel(background_tasks: BackgroundTasks, api_key: str = Security(dependencies.get_api_key_)):

    range_name = dataset_manager.get_excel_range
    
    all_new_values = google_spreadsheet.read_excel(str(range_name), enum=True)
    await dataset_manager.update_dataset_status(all_new_values)

    return {"status":"success", "message":"Dataset updated", "values":range_name}

@app.patch("/update_columns_", description=r"Método interno que se encarga de leer los nombres de las columnas del exce, el estado y actualizar (si es necesario), el archivo de configuración en caso de haber cambios", tags=["Gestor Dataset"], include_in_schema=False)
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


@app.post("/api_set_conf/{token_beaber}", description="Metodo interno para aplicar la configuración", tags=["Sessions"])
async def set_api_cong(token_beaber: str, request: schemas.ApiConf, api_key: str = Security(dependencies.get_api_key_)):

    # Autenticate token
    username, role, id_ = await authenticate_token(token_beaber)

    # Vadilate credentials
    result = await crud.vadilate_user_credentials(username, role, id_)
    if result[0] != id_:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="EL token es incorrecto",
        )
   
    if True: 
        config['DEFAULT']['apikey'] = request.apikey
        config['DEFAULT']['host'] = request.host
        config['DEFAULT']['port'] = request.port
        
        config['EMAIL']['email_sender'] = request.email_sender
        config['EMAIL']['app_password'] = request.app_password
        config['EMAIL']['email_reciver'] = request.email_reciver

        config['API-OAUTH2']['username'] = request.username
        config['API-OAUTH2']['password'] = request.password

        config['GOOGLE-SHEET']['spreadsheed_id'] = request.spreadsheetID

        # Actualizar registros
        with open(Path('conf.ini'), 'w') as configfile:
            config.write(configfile)

    return JSONResponse({'status':'succes','response':'La nueva configuración ha sido cambiada correctamente'})

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


@app.get("/code", description="Redirect URI for API authentication", tags=["Seguridad"])
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


@app.post("/token", description="Crear token de sessión de la forma más segura possible", tags=["Seguridad"])
async def user_create_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    api_key: str = Security(dependencies.get_api_key_)
    ):

    # Authenticate user
    auth_user, role, id_ = await autenticate_user(form_data.username, form_data.password)
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create token session from the token data recived
    data = {"sub":form_data.username, "role": role, "id":str(id_)}
    expire_data = datetime.timedelta(days=120) # Token expires in 120 days
    acces_token = create_access_token(data, expire_data)

    # Set token as cookie
    response.set_cookie(key="token_beaber", value=acces_token)
    return {"access_token":acces_token, "token_type": "bearer"}


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