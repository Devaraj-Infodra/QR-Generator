import qrcode, sys, json, os, requests

def send_sms(phone):
    api_key = os.environ['FAST2SMS_API_KEY']

    if phone.startswith('+91'):
        phone = phone[3:]
    elif phone.startswith('+'):
        phone = phone[1:]

    response = requests.post(
        'https://www.fast2sms.com/dev/bulkV2',
        headers={
            'authorization': api_key,
            'Content-Type': 'application/json'
        },
        json={
            'route': 'q',
            'message': 'hi',
            'language': 'english',
            'flash': 0,
            'numbers': phone
        }
    )
    print(f"SMS status: {response.status_code}")
    print(f"SMS response: {response.text}")

def generate_qr(payload):
    qr_text = f"Name: {payload['title']}\nID: {payload['details']}\nPhone: {payload['phone']}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
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

    send_sms(payload['phone'])

    return raw_url

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    generate_qr(payload)
