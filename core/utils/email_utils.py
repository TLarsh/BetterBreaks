from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from django.conf import settings



# -------------------SEND EMAIL ------------

def send_otp_email(email, otp):
    try:
        brand_name = "Better Breaks"

        # Email subject & body
        subject = f"{brand_name} - Your Password Reset OTP"
        body = f"""
        <html>
            <body>
                <h2 style="color:#4CAF50;">{brand_name}</h2>
                <p>Hello,</p>
                <p>Your One-Time Password (OTP) for password reset is:</p>
                <h3 style="color:#ff6600;">{otp}</h3>
                <p>This code will expire in 10 minutes.</p>
                <br>
                <p>Thank you,</p>
                <p><strong>{brand_name} Team</strong></p>
            </body>
        </html>
        """

        # Email configuration
        from_email = settings.EMAIL_USER
        to_email = email

        # Create MIME message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{brand_name} <{from_email}>"
        msg["To"] = to_email
        msg.attach(MIMEText(body, "html"))

        # Decide between SSL or TLS
        if getattr(settings, "EMAIL_USE_SSL", False):
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        else:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            if getattr(settings, "EMAIL_USE_TLS", False):
                server.starttls()

        # Login & send
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()

        return True, f"OTP sent successfully to {email}"

    except smtplib.SMTPAuthenticationError:
        return False, "SMTP Authentication failed. Check your EMAIL_USER and EMAIL_PASSWORD."
    except smtplib.SMTPConnectError:
        return False, "SMTP Connection failed. Check EMAIL_HOST and EMAIL_PORT."
    except Exception as e:
        return False, f"Unexpected error while sending OTP: {str(e)}"

