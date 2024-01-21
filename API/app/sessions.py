from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi import HTTPException
from uuid import UUID
from . import schemas

cookie_params = CookieParameters()
backend = InMemoryBackend[UUID, schemas.SessionData]()


# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

class BasicVerifier(SessionVerifier[UUID, schemas.SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, schemas.SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception


    def verify_session(self, model: schemas.SessionData):
        '''If the session exists, it is valid (in the furure change this but has to return a boolean'''
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)



import requests

url = 	"http://inutil.com/login"
headers = {
 "api-key":"rmpxCixzGRet81UnltZUBLdURHhnJy4QSltELa6HjU8="
}
data = {
"username":"root",
"password":"mierda69"
}


res = requests.post(url, headers=headers, json=data)
print(res);print(res.text)