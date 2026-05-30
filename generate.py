import qrcode, sys, json
from io import BytesIO

def generate_qr(payload):
    # Format all info into the QR content
    qr_text = f"""Name: {payload['title']}
ID: {payload['details']}
Phone: {payload['phone']}"""

    qr = qrcode.QRCode(version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10, border=4)
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(payload['qr_name'] + ".png")
    print("QR generated: " + payload['qr_name'] + ".png")

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    generate_qr(payload)
