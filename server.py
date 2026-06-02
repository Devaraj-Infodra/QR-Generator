from flask import Flask, request
from twilio.rest import Client
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "QR Server Running"

@app.route("/scan")
def scan():

    phone = request.args.get("phone")

    if not phone:
        return "Phone number missing", 400

    account_sid = os.environ["TWILIO_SID"]
    auth_token = os.environ["TWILIO_TOKEN"]
    from_number = os.environ["TWILIO_FROM"]

    client = Client(account_sid, auth_token)

    if not phone.startswith("+"):
        phone = "+91" + phone

    client.messages.create(
        body="Your QR code was scanned.",
        from_=from_number,
        to=phone
    )

    return "SMS Sent"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
