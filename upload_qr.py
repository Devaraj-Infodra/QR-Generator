import qrcode, sys, json, os, requests
from io import BytesIO

def get_token():
    tenant_id = os.environ['TENANT_ID']
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }
    r = requests.post(url, data=data)
    return r.json()["access_token"]

def generate_qr_bytes(payload):
    qr_text = f"Name: {payload['title']}\nID: {payload['details']}\nPhone: {payload['phone']}"
    qr = qrcode.QRCode(version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10, border=4)
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def upload_to_sharepoint(token, site_hostname, img_bytes, filename):
    # Get site ID
    site_url = f"https://graph.microsoft.com/v1.0/sites/{site_hostname}"
    headers = {"Authorization": f"Bearer {token}"}
    site = requests.get(site_url, headers=headers).json()
    site_id = site["id"]

    # Get default drive
    drives = requests.get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives", headers=headers).json()
    drive_id = drives["value"][0]["id"]

    # Upload file
    upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/QR-Images/{filename}.png:/content"
    headers["Content-Type"] = "image/png"
    r = requests.put(upload_url, headers=headers, data=img_bytes)
    result = r.json()
    file_url = result.get("webUrl", "")
    print(f"FILE_URL={file_url}")
    return file_url

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    token = get_token()
    img_bytes = generate_qr_bytes(payload)
    site = os.environ['SHAREPOINT_SITE']
    upload_to_sharepoint(token, site, img_bytes, payload['qr_name'])
