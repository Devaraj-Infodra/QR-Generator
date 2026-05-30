import qrcode, sys, json, os, requests
from io import BytesIO
import base64

def generate_qr_bytes(payload):
    qr_text = f"Name: {payload['title']}\nID: {payload['details']}\nPhone: {payload['phone']}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    img_bytes = generate_qr_bytes(payload)
    b64 = base64.b64encode(img_bytes).decode()
    
    # Send back to Power Automate callback URL
    callback_url = payload['callback_url']
    r = requests.post(callback_url, json={
        "qr_base64": b64,
        "qr_name": payload['qr_name'],
        "item_id": payload['item_id']
    })
    print("Callback response:", r.status_code)
