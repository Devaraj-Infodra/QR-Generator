import qrcode, sys, json, os
from twilio.rest import Client

def send_sms(phone_field):
    account_sid = os.environ['TWILIO_SID']
    auth_token = os.environ['TWILIO_TOKEN']
    from_number = os.environ['TWILIO_FROM']

    client = Client(account_sid, auth_token)
    numbers = [p.strip() for p in phone_field.split(',')]

    for phone in numbers:
        if not phone.startswith('+'):
            phone = '+91' + phone
        try:
            message = client.messages.create(
                body='Hi',
                from_=from_number,
                to=phone
            )
            print(f"SMS sent to {phone} — SID: {message.sid}")
        except Exception as e:
            print(f"Failed to send to {phone}: {e}")

def generate_qr(payload):
    qr_text = f"Name: {payload['title']}\nID: {payload['details']}\nPhone: {payload['phone']}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    os.makedirs("qr-images", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    path = f"qr-images/{payload['qr_name']}.png"
    img.save(path)

    raw_url = f"https://raw.githubusercontent.com/Devaraj-Infodra/QR-Generator/main/{path}"

    result = {
        "item_id": payload["item_id"],
        "qr_name": payload["qr_name"],
        "qr_url": raw_url
    }
    with open(f"results/{payload['qr_name']}.json", "w") as f:
        json.dump(result, f)

    print(f"QR saved: {path}")
    print(f"URL: {raw_url}")

    return raw_url

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    generate_qr(payload)