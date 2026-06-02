import qrcode, sys, json, os
from twilio.rest import Client

def send_sms(phone_field):
    account_sid = os.environ['TWILIO_SID']
    auth_token  = os.environ['TWILIO_TOKEN']
    from_number = os.environ['TWILIO_FROM']
    client = Client(account_sid, auth_token)
    numbers = [p.strip() for p in phone_field.split(',')]
    for phone in numbers:
        if not phone.startswith('+'):
            phone = '+91' + phone
        try:
            message = client.messages.create(
                body='Your QR code was just scanned!',
                from_=from_number,
                to=phone
            )
            print(f"SMS sent to {phone} — SID: {message.sid}")
        except Exception as e:
            print(f"Failed to send to {phone}: {e}")

def generate_qr(payload):
    # Your Render server URL
    SERVER_URL = "https://qr-generator-q6o8.onrender.com"  # ← change to your Render URL

    item_id = payload["item_id"]
    qr_name = payload["qr_name"]
    phone   = payload["phone"]

    # QR encodes the scan URL — scanning this triggers SMS
    scan_url = f"{SERVER_URL}/scan?id={item_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(scan_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    os.makedirs("qr-images", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    img.save(f"qr-images/{qr_name}.png")

    # Save phone in results JSON so server.py can fetch it on scan
    result = {
        "item_id": item_id,
        "qr_name": qr_name,
        "phone": phone,          # ← this is what server.py needs
        "scan_url": scan_url
    }
    with open(f"results/{item_id}.json", "w") as f:   # ← filename is item_id, not qr_name
        json.dump(result, f, indent=2)

    print(f"QR saved: qr-images/{qr_name}.png")
    print(f"Scan URL: {scan_url}")

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    generate_qr(payload)