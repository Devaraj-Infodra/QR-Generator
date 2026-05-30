import qrcode, sys, json, os
from io import BytesIO

def generate_qr(payload):
    qr_text = f"Name: {payload['title']}\nID: {payload['details']}\nPhone: {payload['phone']}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    path = f"qr-images/{payload['qr_name']}.png"
    img.save(path)
    print(f"QR_PATH={path}")
    raw_url = f"https://raw.githubusercontent.com/Devaraj-Infodra/QR-Generator/main/{path}"
    print(f"QR_URL={raw_url}")
    return raw_url

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    generate_qr(payload)
