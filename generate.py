import qrcode
import sys
import base64
import json
from io import BytesIO

def generate_qr(data: str, qr_name: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    return img_base64

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    data = payload.get("details", "")
    qr_name = payload.get("qr_name", "qr_code")
    
    result = generate_qr(data, qr_name)
    print(json.dumps({"qr_base64": result, "qr_name": qr_name}))