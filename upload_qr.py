import qrcode, sys, json, os

def generate_qr(payload):
    SERVER_URL = "https://qr-generator-q6o8.onrender.com"
    item_id = payload["item_id"]
    qr_name = payload["qr_name"]
    phone   = payload["phone"]

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

    result = {
        "item_id": item_id,
        "qr_name": qr_name,
        "phone": phone,
        "scan_url": scan_url
    }
    with open(f"results/{item_id}.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"QR saved: qr-images/{qr_name}.png")
    print(f"Scan URL: {scan_url}")

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    generate_qr(payload)