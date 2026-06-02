from flask import Flask, request
from upload_qr import send_sms

app = Flask(__name__)

@app.route("/scan")
def scan():
    phone = request.args.get("phone")
    send_sms(phone)
    return "SMS sent!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
