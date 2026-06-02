import os
import requests
from flask import Flask, request, render_template_string
from upload_qr import send_sms

app = Flask(__name__)

# Base URL where GitHub stores your raw result files
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Devaraj-Infodra/QR-Generator/main/results"

@app.route("/scan")
def scan():
    item_id = request.args.get("id")
    if not item_id:
        return "Error: Missing ID parameter.", 400
        
    try:
        # Fetch the JSON payload associated with this scan from your GitHub repo
        response = requests.get(f"{GITHUB_RAW_BASE}/{item_id}.json")
        
        if response.status_code != 200:
            return f"Error: QR record for ID {item_id} not found on server.", 404
            
        data = response.json()
        phone_number = data.get("phone")
        
        if phone_number:
            # Trigger the SMS sending logic
            send_sms(phone_number)
            
            # User-friendly success message displayed on mobile screen
            return render_template_string("""
                <html>
                    <head><title>Scan Successful</title></head>
                    <body style="text-align: center; font-family: sans-serif; padding-top: 50px;">
                        <h1 style="color: #2e7d32;">✓ Scan Confirmed</h1>
                        <p>An SMS notification has been sent to the registered user.</p>
                    </body>
                </html>
            """)
        else:
            return "Error: No phone number linked to this QR record.", 400
            
    except Exception as e:
        return f"An internal server error occurred: {str(e)}", 500

if __name__ == "__main__":
    # Render binds to port 10000 by default, falls back to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
