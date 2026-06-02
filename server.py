from flask import Flask, request
from upload_qr import send_sms

app = Flask(__name__)

@app.route("/scan")
def scan():
    phone = request.args.get("phone")
    send_sms(phone)
    return "SMS sent!"
