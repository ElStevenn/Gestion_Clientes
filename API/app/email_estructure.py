#!/usr/bin/env python3

from configparser import ConfigParser
from pathlib import Path

class GenerateLink:
    def __init__(self):
        pass

    def main(self):
        pass


class ClienteEmailFormatter:
    """
    Clase para formatear datos de clientes en JSON para su uso en correos electrónicos.
    """
    def __init__(self):
        config = ConfigParser()
        config.read(Path("./conf.ini"))
        self.server_ip = config['DEFAULT']['host']
        self.puerto = config['DEFAULT']['port']

    def format_email(self, json_data):
        numero_de_clientes = len(json_data)
        email_body = f"<h2>Tens {numero_de_clientes} {'clients' if numero_de_clientes > 1 else 'client'} {'nous' if numero_de_clientes > 1 else 'nou'}:</h2>"

        for cliente in json_data:
            email_body += f"<div style='margin-bottom: 20px;'>{self._format_cliente_info(cliente)}</div>"
            email_body += "<hr>"

        return str(numero_de_clientes), self._add_email_template(email_body)

    def _format_cliente_info(self, cliente_info):
        formatted_info = (
            f"<p><strong>Nom:</strong> {cliente_info.get('nombre', 'N/A')}<br>"
            f"<strong>Cognoms:</strong> {cliente_info.get('apellidos', 'N/A')}<br>"
            f"<strong>Número de telèfon:</strong> {cliente_info.get('numero_telefono', 'N/A')}<br>"
            f"<strong>Codi postal:</strong> {cliente_info.get('codigo_postal', 'N/A')}<br>"
            f"<strong>Url Registro:</strong> <a href='{cliente_info.get('url_registro', 'N/A')}'>{cliente_info.get('url_registro', 'N/A')}</a><br>"
        )

        informacion_adicional = cliente_info.get("informacion_adicional", {})
        if informacion_adicional:
            formatted_info += "<ul>"
            for key, value in informacion_adicional.items():
                key_formatted = key.replace("_", " ").capitalize()
                formatted_info += f"<li><strong>{key_formatted}:</strong> {value}</li>"
            formatted_info += "</ul>"

        return formatted_info

    def _add_email_template(self, email_body):
        # Se ha eliminado la etiqueta <script> para evitar problemas con los clientes de correo electrónico.
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
    
    



    formatter = ClienteEmailFormatter()
    cantidad_clientes, email_estructurado = formatter.format_email(json_data)
    print(email_estructurado)



