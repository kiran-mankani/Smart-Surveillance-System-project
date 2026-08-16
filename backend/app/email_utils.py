import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_otp_email(receiver_email, otp):

    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    try:
        message = EmailMessage()

        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Smart Surveillance System - OTP"

        message.set_content(
            f"""
Your Smart Surveillance System OTP is:

{otp}

Please do not share this OTP with anyone.
"""
        )

        with smtplib.SMTP("smtp.gmail.com", 587) as server:

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            server.send_message(message)

        print("✅ EMAIL SENT TO:", receiver_email)

        return True

    except Exception as e:

        print("❌ EMAIL FAILED:", str(e))

        return False