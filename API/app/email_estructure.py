#!/usr/bin/env python3

from configparser import ConfigParser
from pathlib import Path
from .email_sender import EmailSender

class ClienteEmailFormatter:
    """
    Clase para formatear datos de clientes en JSON para su uso en correos electrónicos.
    """
    def __init__(self):
        config = ConfigParser()
        config.read(Path("./conf.ini"))
        self.server_ip = config['DEFAULT']['host']
        self.puerto = config['DEFAULT']['port']

    def format_email(self, *json_data):
        numero_de_clientes = len(json_data)
        email_body = f"<h2>Tienes {numero_de_clientes} {'clientes' if numero_de_clientes > 1 else 'cliente'} {'nuevos' if numero_de_clientes > 1 else 'nuevo'}:</h2>"
        email_subject = f"Tienes {numero_de_clientes} {'clienes' if numero_de_clientes > 1 else 'cliente'} a responder"

        for single_client in json_data[0]: 
            email_body += f"<div style='margin-bottom: 20px;'>{self._format_cliente_info(**single_client)}</div>"
            email_body += "<hr>"

        return email_subject, self._add_email_template(email_body)

    def _format_cliente_info(self, **client_info):
        result = ""

        for key, value in client_info.items():
            if isinstance(value, dict):  
                result += "<ul>"
                for k_, v_ in value.items():
                    result += f"<li><strong>{k_}:</strong> {self._format_value(v_)}</li>"
                result += "</ul>"
            else:
                result += f"<p><strong>{key}:</strong> {self._format_value(value)}<br>\n"

        return result

    def _format_value(self, value):
        if isinstance(value, dict):
            return ''.join(f"<li><strong>{k}:</strong> {self._format_value(v)}</li>" for k, v in value.items())
        return str(value)

    def _add_email_template(self, email_body):
        return f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }}
                    h2 {{
                        color: #333;
                    }}
                    p, li {{
                        color: #555;
                    }}
                    a {{
                        color: #06c;
                        text-decoration: none;
                    }}
                    div {{
                        background-color: #fff;
                        padding: 15px;
                        margin-bottom: 10px;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    }}
                    hr {{
                        border: 0;
                        height: 1px;
                        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));
                        margin-top: 20px;
                        margin-bottom: 20px;
                    }}
                </style>
            </head>
            <body>
                {email_body}
            </body>
        </html>
        """



def new_client_send_email(dict_data: dict):
    _email_sender = EmailSender("./conf.ini") 
    email_formatter = ClienteEmailFormatter()

    subject, structed_email = email_formatter.format_email(dict_data)

    _email_sender.send_email("sfukinguay@gmail.com", subject, structed_email)

if __name__ == "__main__":
    
    # Ejemplo de uso de la clase
    json_data = [
        {
        "nombre": "NombreDelCliente",
        "apellidos": "ApellidosDelCliente",
        "numero_telefono": "123456789",
        "codigo_postal": "08001",
        "url_registro": "http://example.com/registro",
        "informacion_adicional": {
            "fecha_de_contacto": "2023-11-12",
            "resultado": "Contrata"  
        }
        },
        {
        "nombre": "NombreDelCliente2",
        "apellidos": "ApellidosDelCliente2",
        "numero_telefono": "987654321",
        "codigo_postal": "08001",
        "url_registro": "http://example.com/registro2",
        "informacion_adicional": {
            "fecha_de_contacto": "2023-11-14",
            "resultado": "Contrata"  
        }
        }
    ]
    
    



    new_client_send_email(json_data)



