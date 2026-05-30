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
    print("Token response:", r.status_code, r.text[:200])
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

def upload_to_sharepoint(token, img_bytes, filename):
    headers = {"Authorization": f"Bearer {token}"}

    # Get site ID
    site_url = "https://graph.microsoft.com/v1.0/sites/infodratechnologies.sharepoint.com:/sites/IoT-Proto"
    site_resp = requests.get(site_url, headers=headers)
    print("Site response:", site_resp.status_code, site_resp.text[:300])
    site_data = site_resp.json()

    if "id" not in site_data:
        raise Exception(f"Could not get site ID: {site_data}")

    site_id = site_data["id"]

    # Get drives
    drives_resp = requests.get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives", headers=headers)
    print("Drives response:", drives_resp.status_code, drives_resp.text[:300])
    drives = drives_resp.json()

    # Find QR-Images drive
    drive_id = None
    for drive in drives.get("value", []):
        print("Drive found:", drive.get("name"))
        if drive.get("name") == "QR-Images":
            drive_id = drive["id"]
            break

    if not drive_id:
        drive_id = drives["value"][0]["id"]
        print("Using default drive:", drive_id)

    # Upload file
    upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{filename}.png:/content"
    headers["Content-Type"] = "image/png"
    r = requests.put(upload_url, headers=headers, data=img_bytes)
    print("Upload response:", r.status_code, r.text[:300])
    result = r.json()
    file_url = result.get("webUrl", "")
    print(f"FILE_URL={file_url}")
    return file_url

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    token = get_token()
    img_bytes = generate_qr_bytes(payload)
    upload_to_sharepoint(token, img_bytes, payload['qr_name'])
