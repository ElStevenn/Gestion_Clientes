#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
<<<<<<< HEAD
# from fastapi_sessions.session_verifier import SessionVerifier
from fastapi.logger import logger
from starlette.websockets import WebSocketDisconnect
from app import schemas, dependencies, email_sender, email_estructure, datasets_manager, documentation_others, security, google_sheet_imp
from app.security import aes_encrypter # Encrypter
from fastapi_redis_session import deleteSession, getSession, getSessionId, getSessionStorage, setSession, SessionStorage
from typing import Optional, Annotated, Any
=======
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi.logger import logger
from starlette.websockets import WebSocketDisconnect
from app import schemas, dependencies, email_sender, email_estructure, datasets_manager, documentation_others, security, sessions
from typing import Optional, Annotated
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066
from configparser import ConfigParser
import os, datetime
import uvicorn
from uuid import uuid4
from uuid import UUID
from pathlib import Path
<<<<<<< HEAD
import google_auth_oauthlib.flow
=======

>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066

app = FastAPI(
    title="API Gestión de Prospectos i Comunicaciónes Empresariales",
    summary = "",
    description="\nEstá API diseñada para optimizar la interacción con clientes potenciales y la comunicación empresarial. Funciona recibiendo datos desde una fuente externa, gestionando estos inputs para identificar clientes con potencial. A continuación, automatiza el envío de correos electrónicos a estos clientes, facilitando un seguimiento efectivo. Paralelamente, la API permite a la empresa responder rápidamente sobre el interés en un cliente, verificar la precisión de los datos o actualizar información relevante. Esta interfaz API es una herramienta clave para empresas que buscan mejorar su gestión de relaciones con clientes y optimizar las comunicaciones comerciales.",
<<<<<<< HEAD
    version="0.1",
    docs_url="/docs_00"
=======
    version="0.1"
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066
)

# Configuración de rutas y directorios
base_dir = Path(__file__).parent
static_dir = os.path.join(base_dir, 'frontend', 'static')
app.mount("/static", StaticFiles(directory=static_dir), name="static")

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

<<<<<<< HEAD
# aes_encrypter = security.AESEncryptionW_256(Path("app/keys/key_admin.txt")) # Classe para encriptar y desencriptar con AES 256

# Google spreadsheet
google_spreadsheet = google_sheet_imp.Document_CRUD()
google_spreadsheet.Spreadsheet_ID = config['GOOGLE-SHEET']['spreadsheet_id']

=======
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066
# Define cores
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
<<<<<<< HEAD
    "http://paumateu.top",
    "http://inutil.top/",
    "http://185.254.206.129/"
=======
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066
]

app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=origins,  # Luego si quiero puedo especificar los orígenes exactos en la production.
=======
    allow_origins=["*"],  # Luego si quiero puedo especificar los orígenes exactos en la production.
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Delete the debug
import logging
from uvicorn.config import logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("This log message will always show up.")

<<<<<<< HEAD

# ----------------------------- Gestión de excepciones y Validaciones -------------------------------------

@app.exception_handler(RequestValidationError)
async def vadilation_exception_handler(request: Request, exc: RequestValidationError):
=======
# ----------------------------- Gestión de excepciones y Validaciones -------------------------------------

@app.exception_handler(RequestValidationError)
async def vadilation_exception_handler(request, exc: RequestValidationError):
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066
    """Manejar excepciones para RequestValidationError."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

<<<<<<< HEAD
=======

>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066
# ----------------------------- Distintas solicitudes de la API -----------------------------

@app.get("/", description="Función root. Esta función comprueba que la API esté en funcionamiento")
def root_conf():
    return {"response":f"api de gestioón y prospectos empresariales"}



@app.post("/enviar_cliente", description = documentation_others.enviar_cliente_doc)
async def enviar_client(request: schemas.ClientsRequest, api_key = str(Depends(dependencies.get_api_key))):
    count = 0
    mail_structure_dict = []
    
    # Comprovar si hay algún dato duplicado

    


    # Esta parte se encarga de guardar el cliente en un dataset
    for client in request.clientes:

        # Asegurarse que el nombre de  las columnas sean correctas 
        row_body = {
            'id': str(uuid4()),
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
       
        await dataset_manager.add_new_row(row_body)
        count +=1
        mail_structure_dict.append(row_body)
    
    # Parte que se encarga de estructurar y enviar el correo electronico
    # clients_dict = [client.dict() for client in request.clientes]
    cantidad_clientes, email_estructurado = email_structure.format_email(mail_structure_dict)
    
    email_subject = f"Tens {int(cantidad_clientes)} {'clients' if int(cantidad_clientes) > 1 else 'client'} {'nous' if int(cantidad_clientes) > 1 else 'nou'} a respondre"

    _email_sender.send_email(receiver_email=config['EMAIL']['email_reciver'], subject=str(email_subject), message_body=email_estructurado)

    if count > 0: 
        return {"status": "success", "response": "Email enviado correctamente"} # "Los clientes han sido recividos, y email enviado correctamente"
    else:
        return {"status": "error", "response":"No has introducido ningún cliente en el cuerpo de la solicitud, mira el cuerpo de la solicitud"}



@app.get("/client_manual_response/", response_class=HTMLResponse, description="Método interno que redirecciona a una  página para rellenar los datos")
async def resonder_cliente_inter(request: Request, id: Optional[str] = ''):


    return templates.TemplateResponse("client_verifier_page.html", {'request': request,"name":"Nombre_Cliente", "client_id":id}) # Pasar luego el id del cliente real aquí

@app.get("/responder_cliente/", response_class=HTMLResponse, description="Página aparte que te sale para abrir una pestaña aparte para responder la solicitud")
async def client_html_response(request: Request, id: Optional[str] = ''):


    return templates.TemplateResponse("client_camps_verify.html", {'request': request}) # Agregar más campos aquí 


@app.get("/veure_usuaris/", response_class=HTMLResponse, description="Interfaz HTML que porporciona la API para ver los usuarios.\n\n**Parámetros de Entrada:**\n- **pag**: (Opcional) Es un entero que representa el número de página en la paginación de la tabla. Si no se proporciona, por defecto es 1")
async def veure_dataset(request: Request, pag: Optional[int] = 1):
    
    # Obtengo la posición actual de los botones
    buttons_position = datasets_manager.ButtonManager.get_actual_position(pag-1)


    return templates.TemplateResponse('dataset_visualize.html', {"request": request, "button_var": buttons_position, "num_page": pag-1, "server_ip": host, "nombre_columna_reservada": documentation_others.del_guiones(config['OTROS']['nombre_columna_reservada'])})



@app.get("/get_json_dataset", description="Este método es interno y se encarga de pasar los datos en formato JSON para su posterior utilización en tablas.")
async def get_json_dataset(api_key = str(Depends(dependencies.get_api_key))):

    json_dataset = dataset_manager.dataset_toJson

    return json_dataset


@app.get("/admin_response", response_class=HTMLResponse, description="Esta es la página del link para que pueda responder la respuesta el admin")
async def admin_accept_response(request: Request, id: Optional[str] = "" , api_key = str(Depends(dependencies.get_api_key))):

    return templates.TemplateResponse('client_verifier_page.html', {"request": request, "variable1": "this is a great variable"})


@app.get("/descargar_tabla", description="Este método es interno, y es usado para mandar al frontend el para descargar la tabla")
async def download_table(filename: Optional[str] = "Tabla_clientes.xlsx" ,api_key = str(Depends(dependencies.get_api_key))):

    return FileResponse(dataset_manager.get_xlsx_document(filename))


@app.get("/apiconf", response_class=HTMLResponse, description="Pequeño panel html para configurar la API (hacer si me da tiempo)") # response_class=HTMLResponse, 
async def api_conf(request: Request):
<<<<<<< HEAD
    
    # Poner aquí la redirección en vez de en el frontend
=======
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066

    return templates.TemplateResponse(
        'api_conf.html', {
            'request': request, 'apikey':api_key, 'email_sender': config['EMAIL']['email_sender'], 'host':host, 'port': port,'app_password':config['EMAIL']['app_password'],
            'email_reciver':config['EMAIL']['email_reciver'], 'max_columnas_frontend': config['OTROS']['max_columnas_frontend'], 'nombre_columna_reservada': config['OTROS']['nombre_columna_reservada'],
<<<<<<< HEAD
            'username': config['API-OAUTH2']['username'], 'password': config['API-OAUTH2']['password'], 'spreadsheetID': config['GOOGLE-SHEET']['spreadsheet_id']
            }
        )

@app.post("/login")
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

@app.post("/get-session", description="Obtener la session actual")
async def get(session: Any = Depends(getSession)):
    return session


@app.post("/set-session", description="Crear una nueva session")
async def set(request: Request, response: Response, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    sessionData = await request.json()
    sessionId = setSession(response, sessionData, sessionStorage)
    
    response.set_cookie(key="session_id", value=sessionId, httponly=True, secure=False, samesite='Lax')
    return {"session": f"{sessionData}", "message":f"session has been created succesfully", "session_id":sessionId}


@app.get("/expire-session", description="")
async def get(sessionId: str = Depends(getSessionId), sessionStorage: SessionStorage = Depends(getSessionStorage)):
    deleteSession(sessionId, sessionStorage)
    return None
=======
            'username': config['API-OAUTH2']['username'], 'password': config['API-OAUTH2']['password']
            }
        )

@app.post("/create_session")
async def create_session(body_request: schemas.UserLoginBasicBody, response: Response):

    # Verify body_request
    verification_result = await check_username(body_request)
    if verification_result['response'] == "failed":
        return {"status":"failed", "response": verification_result['message']}
    
    # Create session
    # session = uuid4()
    # data = schemas.SessionData(username=body_request.username, token=security.create_acces_token(data={"username":body_request.username, "password":body_request.password})) 

    
    # await sessions.backend.create(session, data=data)
    # sessions.cookie.attach_to_response(response, session)

    return {"status":"sucsess","response":f"created session for {body_request.username}"}

@app.get("/whoami", dependencies=[Depends(sessions.cookie)], description="Devuelve los datos de session sobre cuál sessione está el usuario")
async def whoami(session_data: schemas.SessionData = Depends(sessions.verifier)):
    return {"response":session_data}

@app.post("/delete_session")
async def delete_session(response: Response, session_id: UUID = Depends(sessions.cookie)):
    await sessions.backend.delete(session_id)
    sessions.cookie.delete_from_response(response)
    return {"response":"deleted session"}
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066

@app.get("/api_conf_login", response_class=HTMLResponse, description="Verificacion del usuario para acceder a la apiconf")
async def api_conf_login(request: Request, redirect: Optional[str] = None):
    
    return templates.TemplateResponse('client_verify.html', {'request': request, 'redirect':redirect})

<<<<<<< HEAD
@app.post("/check_username", description="Método interno para verificar si el usuario es correcto y existe")
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
=======
@app.post("/check_username", description="Método interno para verificar si el usuario es correcto")
async def check_username(body_request: schemas.UserLoginBasicBody, api_key=str(Depends(dependencies.get_api_key))):


    # Check if body_reuest.username exists into the fake database (in the future i'll use a real database but now i don't have enough time)
    user = security.get_user_db(security.fake_users_db2, body_request.username)
    if not user or user.disabled:
        return {"response":"failed", "message": f"User \"{body_request.username}\" doesn't exists or is inactive"}

    # In the future check if token is valid, because it's likely the token could be expired


    # Check if password is correct through its token and if valid
    decoded_password = security.decode_token(user.hashed_password)
    if decoded_password['password'] != body_request.password:
        return {"response":"failed", "message": f"Password it's incorrect!"}

    return {"response":"succes", "message": f"User {body_request.username} has been verified sucessfully"}
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066


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

<<<<<<< HEAD
        config['GOOGLE-SHEET']['spreadsheed_id'] = request.spreadsheetID

=======
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066
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


<<<<<<< HEAD
# ------------------- OAuth2 Autentication ----------------------------------------------------------------

@app.get("/code", description="Redirect URI for API authentication", tags="OAuth2")
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

=======
@app.websocket("/wp_apiconf")
async def websocket_apiconf_endpoint(websocket: WebSocket):
    """Websocket para enviar los datos de configuración21"""
    await websocket.accept()
    try:
        while True:
            data_response = await websocket.receive_text() # En principio recivirá un texto de confirmación de aceptación del socket

            if data_response == 'get_apiconf':
                json_data_response = {
                    'apikey':api_key, 'email_sender': config['EMAIL']['email_sender'], 'host':host, 'port': port,'app_password':config['EMAIL']['app_password'],
                    'email_reciver':config['EMAIL']['email_reciver'], 'max_columnas_frontend': config['OTROS']['max_columnas_frontend'], 'nombre_columna_reservada': config['OTROS']['nombre_columna_reservada'],
                    'username': config['API-OAUTH2']['username'], 'password': config['API-OAUTH2']['password']
                }

                await websocket.send_json(json_data_response)

    except WebSocketDisconnect as e:
        print(f"Client apiconf disconected with code: {e.code}")

# ------------------- OAuth2 Autentication ----------------------------------------------------------------

>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066

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

<<<<<<< HEAD
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
=======
@app.post("/token", description="Token endpoint for user authentication")
async def login(from_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = security.get_user_db(security.fake_users_db2, from_data.username)

    if not user:
        raise HTTPException(status_code=400, detail=f"Incorrect username or password")
    
    user_val =  security.verify_password(from_data.password, user.hashed_password)
    if not user_val:
        raise HTTPException(status_code=400, detail=f"Incorrect username or password")
    # Generate a token (to be replaced with a real JWT or similar token)
    token = security.create_acces_token(data={"sub":user.username}, expire_delta=datetime.timedelta(days=30)) # At this moment, the token will expires in 30 days

    return {"acces_token": token, "token_type": "bearer"}
 

@app.get("/users/me", description="add description here abot what this functiondoes")
async def read_ysers_me(
    current_user: Annotated[security.User, Depends(get_current_active_user)]
):
    return current_user
>>>>>>> d6981f63b4066d5350a4a69c7248452b31c5d066



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