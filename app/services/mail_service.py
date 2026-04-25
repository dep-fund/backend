import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


class MailService:
   
    def send_reset_password_email(
        self,
        email: str,
        token: str
    ) -> None:
        message = MIMEMultipart()
        message["From"] = settings.SENDER_EMAIL
        message["To"] = email
        message["Subject"] = "Recuperar contraseña - TuApp"

        # 2. Construimos el cuerpo del correo
        body_text = f"""
        <html>
          <body>
            <h1>Recuperar Contraseña</h1>
            <p>Hola,</p>
            <p>Has solicitado restablecer tu contraseña. Usa el siguiente enlace para crear una nueva:</p>
            <a href="http://localhost:8000/reset-password?token={token}">Restablecer Contraseña</a>
            <p>Este enlace expirará en 15 minutos.</p>
            <p>Si no solicitaste esto, ignora este correo.</p>
            <p>Atentamente,<br>TuApp</p>
          </body>
        </html>
        """
        
        message.attach(MIMEText(body_text, "html"))

        # 3. Enviamos el correo (Simulado)
        try:
            print(f"[MOCK EMAIL] Enviando a {email}: {body_text}")
            # Aquí iría tu código real de smtplib o Resend
        except Exception as e:
            # Si falla al enviar, NO lanzamos error para no exponer el usuario
            print(f"[ERROR] No se pudo enviar el correo a {email}: {e}")
        