# import smtplib
# from email.mime.text import MIMEText
# import os
# from dotenv import load_dotenv

# # Load .env
# load_dotenv()

# EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
# EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
# EMAIL_USER = os.getenv("EMAIL_HOST_USER")
# EMAIL_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
# EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "True") == "True"

# # === Config ===
# TO_EMAIL = "fedustechnilogies@gmail.com"  

# def send_test_email():
#     try:
#         msg = MIMEText("This is a test email from Django SMTP configuration.")
#         msg["Subject"] = "SMTP Test"
#         msg["From"] = EMAIL_USER
#         msg["To"] = TO_EMAIL

#         # Connect to SMTP server
#         server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30)
#         if EMAIL_USE_TLS:
#             server.starttls()

#         server.login(EMAIL_USER, EMAIL_PASSWORD)


#         server.sendmail(EMAIL_USER, [TO_EMAIL], msg.as_string())
#         server.quit()

#         print("✅ Email sent successfully!")

#     except smtplib.SMTPAuthenticationError:
#         print("❌ SMTP Authentication failed. Check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD.")
#     except smtplib.SMTPConnectError:
#         print("❌ SMTP Connection failed. Check EMAIL_HOST and EMAIL_PORT.")
#     except Exception as e:
#         print(f"❌ Unexpected error: {e}")

# if __name__ == "__main__":
#     send_test_email()



import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))
EMAIL_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "True") == "True"

TO_EMAIL = "fedustechnologies.com"  
def send_test_email():
    try:

        msg = MIMEText("This is a test email using SSL.")
        msg["Subject"] = "SMTP SSL Test"
        msg["From"] = EMAIL_USER
        msg["To"] = TO_EMAIL

        if EMAIL_USE_SSL:
            server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=30)
        else:
            raise ValueError("EMAIL_USE_SSL is False. Enable it in .env.")

        server.login(EMAIL_USER, EMAIL_PASSWORD)

        server.sendmail(EMAIL_USER, [TO_EMAIL], msg.as_string())
        server.quit()

        print("✅ Email sent successfully using SSL!")

    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication failed. Check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD.")
    except smtplib.SMTPConnectError:
        print("❌ SMTP Connection failed. Check EMAIL_HOST and EMAIL_PORT.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    send_test_email()
