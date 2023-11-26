import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from configparser import ConfigParser
from pathlib import Path

class EmailSender:
    def __init__(self, email_config_path):
        config = ConfigParser()
        config.read(Path(email_config_path))
        self.password = config['EMAIL']['app_password']
        self.email = config['EMAIL']['email_sender']

    def send_email(self, receiver_email, subject, message_body):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email, self.password)

            msg = MIMEMultipart()
            msg.attach(MIMEText(message_body, 'html', 'utf-8'))  # Puesto en formato html, se puede cambiar también a txt
            msg["Subject"] = Header(subject, 'utf-8')
            msg["From"] = self.email
            msg["To"] = receiver_email

            server.sendmail(self.email, receiver_email, msg.as_string())
            print("Email has been sent successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            server.quit()

# Uso de la clase
if __name__ == "__main__":
    email_sender = EmailSender("../conf.ini")
    email_sender.send_email("paumat17@gmail.com", "Hello World", "<b>Sent from Python</b>")
