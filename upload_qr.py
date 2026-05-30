import qrcode, sys, json, os, requests
from io import BytesIO

def get_token():
    tenant_id = os.environ['TENANT_ID']
    client_id = os.environ['CLIENT_ID']
    username = os.environ['SP_USERNAME']
    password = os.environ['SP_PASSWORD']
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "password",
        "client_id": client_id,
        "username": username,
        "password": password,
        "scope": "https://graph.microsoft.com/Sites.ReadWrite.All"
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

def upload_to_sharepoint(token, img_bytes, filename, item_id):
    headers = {"Authorization": f"Bearer {token}"}

    site_url = "https://graph.microsoft.com/v1.0/sites/infodratechnologies.sharepoint.com:/sites/IoT-Proto"
    site_resp = requests.get(site_url, headers=headers)
    print("Site response:", site_resp.status_code, site_resp.text[:300])
    site_data = site_resp.json()

    if "id" not in site_data:
        raise Exception(f"Could not get site ID: {site_data}")

    site_id = site_data["id"]

    drives_resp = requests.get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives", headers=headers)
    drives = drives_resp.json()

    drive_id = None
    for drive in drives.get("value", []):
        if drive.get("name") == "QR-Images":
            drive_id = drive["id"]
            break
    if not drive_id:
        drive_id = drives["value"][0]["id"]

    upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{filename}.png:/content"
    headers["Content-Type"] = "image/png"
    r = requests.put(upload_url, headers=headers, data=img_bytes)
    result = r.json()
    file_url = result.get("webUrl", "")
    print(f"FILE_URL={file_url}")

    # Update SharePoint list item QR Code column
    list_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/QR-Generator/items/{item_id}/fields"
    headers["Content-Type"] = "application/json"
    update_data = {"QR_x0020_Code": file_url, "Status": "Generated"}
    ur = requests.patch(list_url, headers=headers, json=update_data)
    print("Update item response:", ur.status_code, ur.text[:200])

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    token = get_token()
    img_bytes = generate_qr_bytes(payload)
    upload_to_sharepoint(token, img_bytes, payload['qr_name'], payload['item_id'])
