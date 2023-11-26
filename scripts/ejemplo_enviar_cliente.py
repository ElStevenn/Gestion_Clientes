
import requests

"""
Ejemplo de como enviar la solicitud API al método /enviar_cliente.
Tener en cuenta de que la url "http://185.254.206.129/" tiene que ser cambiada por la IP del servidor

"""


# Definir la URL del endpoint
url = "http://185.254.206.129/enviar_cliente"
url2 = "http://185.254.206.129:443/api_set_conf"

# Definir el cuerpo de la solicitud con la información adecuada
body = {
   "clientes":[
    {
      "nombre": "Marc",
      "apellidos": "El Oro y el bitch",
      "numero_telefono": "+34 640523319",
      "codigo_postal": "08901",
      "url_registro": "http://example.com/registro_Pepitero",
      "campo_adicional": "",
      "informacion_adicional": {
        "fecha_de_contacto": "2023-11-12",
        "resultado": "Contrata"  # Este valor debe reflejar el resultado de la interacción real
      }
    }
  ] 
}

body2 = {
  "apikey": "apikey123",
  "host": "0.0.0.0",
  "port": "80",
  "email_sender": "paumat17@gmail.com",
  "app_password": "123456789",
  "email_reciver": "sfukinguay@gmail.com",
  "max_columns_frontend": "33",
  "name_reserved_column": "lol",
  "username": "pepinazo",
  "password": "1234qwerasdf"
}
res = requests.post(url2, params={'api_key': '948373984739874'}, json=body2)
print(res.json())

# # Realizar la solicitud POST incluyendo la API key como parámetro de la URL y el cuerpo JSON
# res = requests.post(url, params={'api_key': '948373984739874'}, json=body)

# # Imprimir la respuesta de la solicitud
# print(res.json())