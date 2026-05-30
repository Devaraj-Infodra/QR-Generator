import qrcode, sys, json, os, requests
from io import BytesIO

def get_token():
    tenant_id = os.environ['TENANT_ID']
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    url = f"https://accounts.accesscontrol.windows.net/{tenant_id}/tokens/OAuth/2"
    data = {
        "grant_type": "client_credentials",
        "client_id": f"{client_id}@{tenant_id}",
        "client_secret": client_secret,
        "resource": f"00000003-0000-0ff1-ce00-000000000000/infodratechnologies.sharepoint.com@{tenant_id}"
    }
    r = requests.post(url, data=data)
    print("Token response:", r.status_code, r.text[:300])
    return r.json()["access_token"]

def generate_qr_bytes(payload):
    qr_text = f"Name: {payload['title']}\nID: {payload['details']}\nPhone: {payload['phone']}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def upload_to_sharepoint(token, img_bytes, filename, item_id):
    site = "https://infodratechnologies.sharepoint.com/sites/IoT-Proto"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json;odata=verbose",
        "Content-Type": "image/png"
    }
    # Upload file
    upload_url = f"{site}/_api/web/GetFolderByServerRelativeUrl('QR-Images')/Files/add(url='{filename}.png',overwrite=true)"
    r = requests.post(upload_url, headers=headers, data=img_bytes)
    print("Upload response:", r.status_code, r.text[:300])
    file_url = f"{site}/QR-Images/{filename}.png"
    print(f"FILE_URL={file_url}")

    # Update list item
    headers["Content-Type"] = "application/json;odata=verbose"
    headers["X-HTTP-Method"] = "MERGE"
    headers["IF-MATCH"] = "*"
    update_url = f"{site}/_api/web/lists/getbytitle('QR-Generator')/items({item_id})"
    body = {"__metadata": {"type": "SP.Data.QR_x002d_GeneratorListItem"}, "QR_x0020_Code": file_url, "Status": "Generated"}
    ur = requests.post(update_url, headers=headers, json=body)
    print("Update item response:", ur.status_code, ur.text[:200])

if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    token = get_token()
    img_bytes = generate_qr_bytes(payload)
    upload_to_sharepoint(token, img_bytes, payload['qr_name'], payload['item_id'])
