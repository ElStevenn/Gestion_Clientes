# !/usr/bin/env python3

# Change the description so that can apear ok and even in the future and can implement it through AI
enviar_cliente_doc = """

Esta función recibe y procesa la información de los clientes potenciales. Esta función es para ser utilizada por sistemas externos que necesitan enviar datos de clientes para su gestión y seguimiento en la plataforma.

### Cuerpo de la Solicitud (Body):

- Debe ser un objeto JSON que contenga una lista de clientes.
- Cada cliente debe incluir los siguientes datos:
  - `nombre`: Nombre del cliente.
  - `apellidos`: Apellidos del cliente.
  - `numero_telefono`: Número de teléfono del cliente.
  - `codigo_postal`: Código postal del cliente.
  - `url_registro`: URL de registro asociada al cliente.
  - `informacion_adicional`: Cualquier información adicional relevante, dentro de un diccionario


"""


def del_guiones(txt):
  return txt.replace('_',' ').replace('-',' ').capitalize()

def replace_spaces(txt):
  return txt.replace(' ','_').capitalize()

