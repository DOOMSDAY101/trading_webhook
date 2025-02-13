import json

from flask import Flask, request, jsonify
import requests
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get API credentials from environment variables
TERMII_API_KEY = os.getenv("TERMII_API_KEY")
TERMII_BASE_URL = "https://v3.api.termii.com"

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
TERMII_SENDER_ID = os.getenv("TERMII_SENDER_ID")

def send_sms(phone_number, message):
    url = f"{TERMII_BASE_URL}/api/sms/send"
    payload = {
        "to": phone_number,
        "from": TERMII_SENDER_ID,
        "sms": message,
        "type": "plain",
        "channel": "generic",
        "api_key": TERMII_API_KEY
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    try:
        response_data = response.json()  # Parse JSON response
    except json.JSONDecodeError:
        return f"Failed to send SMS: Invalid JSON response - {response.text}"

    if response.status_code == 200 and "message" in response_data:
        return response_data["message"]  # Return "Successfully Sent" or similar
    else:
        return f"Failed to send SMS: {response_data.get('message', response.text)}"


# Function to send email using SMTP
def send_email(to_email, subject, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM_EMAIL
        msg["To"] = to_email

        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM_EMAIL, to_email, msg.as_string())
        server.quit()

        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"


# Webhook Endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received data:", data)

    # phone_number = "+2349065304004"
    # email = "georgequin19@gmail.com"
    phone_number = "+2348088890349"
    email = "ifeoluwasulaiman403@gmail.com"
    message = json.dumps(data, indent=2)
    message_str = "\n".join([f"{key}: {value}" for key, value in data.items()])

    # Send SMS and Email
    sms_response = send_sms(phone_number,  message_str) if phone_number else "No phone provided."
    email_response = send_email(email, "Trading Alert!", message) if email else "No email provided."

    return jsonify({
        "status": "success",
        "sms_response": sms_response,
        "email_response": email_response
    }), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
