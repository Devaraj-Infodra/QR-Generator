import qrcode
import sys
import json
import os
from twilio.rest import Client

def send_sms(phone_field):
    account_sid = os.environ['TWILIO_SID']
    auth_token = os.environ['TWILIO_TOKEN']
    from_number = os.environ['TWILIO_FROM']
    client = Client(account_sid, auth_token)
    # Ensure phone_field is treated as a string and handle spaces
    numbers = [p.strip() for p in str(phone_field).split(',')]

    for phone in numbers:
        if not phone.startswith('+'):
            phone = '+91' + phone
        try:
            message = client.messages.create(
                body='Hi, your QR code was successfully scanned!',
                from_=from_number,
                to=phone
            )
            print(f"SMS sent to {phone} — SID: {message.sid}")
        except Exception as e:
            print(f"Failed to send to {phone}: {e}")

def generate_qr(payload):
    # 1. Dynamically read your Render Web Service URL from an environment variable.
    # Replace the fallback link with your actual Render URL once deployment finishes.
    base_url = os.environ.get("FLASK_SERVER_URL", "https://your-render-app-name.onrender.com")
    
    # 2. Secure QR payload using the unique SharePoint item ID instead of exposing plain phone numbers
    qr_text = f"{base_url}/scan?id={payload['item_id']}"
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    os.makedirs("qr-images", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    path = f"qr-images/{payload['qr_name']}.png"
    img.save(path)
    
    raw_url = f"https://raw.githubusercontent.com/Devaraj-Infodra/QR-Generator/main/{path}"

    # 3. Add the 'phone' number here so it saves to the repository metadata
    result = {
        "item_id": payload["item_id"],
        "qr_name": payload["qr_name"],
        "phone": payload["phone"], 
        "qr_url": raw_url
    }
    
    # Save the file using item_id as the name for seamless lookups by the Flask server
    with open(f"results/{payload['item_id']}.json", "w") as f:
        json.dump(result, f)
        
    print(f"QR saved: {path}")
    return raw_url

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    generate_qr(payload)
