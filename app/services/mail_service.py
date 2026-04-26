import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class MailService:
   
    def send_reset_password_email(
        self,
        email: str,
        token: str,
        user_type: str = "STANDARD"
    ) -> None:
        
        base_url = settings.FRONTEND_URL
        if user_type == "ADMIN":
            base_url = settings.BACKOFFICE_URL
            
        reset_link = f"{base_url}/reset-password?token={token}"
        message = MIMEMultipart()
        message["From"] = settings.SENDER_EMAIL
        message["To"] = email
        message["Subject"] = "Recuperar contraseña - DepFund"

        body_text = f"""
        <html>
          <body>
            <h1>Recuperar Contraseña</h1>
            <p>Hola,</p>
            <p>Has solicitado restablecer tu contraseña. Usa el siguiente enlace para crear una nueva:</p>
            <a href="{reset_link}">Restablecer Contraseña</a>
            <p>Este enlace expirará en 15 minutos.</p>
            <p>Si no solicitaste esto, ignora este correo.</p>
            <p>Atentamente,<br>DepFund</p>
          </body>
        </html>
        """
        
        message.attach(MIMEText(body_text, "html"))

        try:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
            server.send_message(message)
            server.quit()
            print(f"[EMAIL] Correo de recuperación enviado exitosamente a {email}")
        except Exception as e:
            print(f"[ERROR] No se pudo enviar el correo a {email}: {e}")