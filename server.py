import os
import requests
from flask import Flask, request, render_template_string


app = Flask(__name__)

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Devaraj-Infodra/QR-Generator/main/results"

@app.route("/scan")
def scan():
    item_id = request.args.get("id")
    if not item_id:
        return "Error: Missing ID.", 400

    try:
        response = requests.get(f"{GITHUB_RAW_BASE}/{item_id}.json")
        if response.status_code != 200:
            return "Record not found.", 404

        data = response.json()
        name = data.get("qr_name", "User")
        phone = data.get("phone", "")

        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Contact</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { margin:0; padding:0; box-sizing:border-box; }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                .card {
                    background: white;
                    border-radius: 24px;
                    padding: 40px 30px;
                    text-align: center;
                    max-width: 360px;
                    width: 100%;
                    box-shadow: 0 25px 60px rgba(0,0,0,0.4);
                }
                .avatar {
                    width: 80px;
                    height: 80px;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 20px;
                    font-size: 36px;
                }
                .company {
                    font-size: 12px;
                    color: #999;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    margin-bottom: 8px;
                }
                h1 {
                    font-size: 24px;
                    color: #1a1a2e;
                    margin-bottom: 6px;
                }
                .id-badge {
                    display: inline-block;
                    background: #f0f0f0;
                    color: #666;
                    font-size: 13px;
                    padding: 4px 12px;
                    border-radius: 20px;
                    margin-bottom: 20px;
                }
                .divider {
                    height: 1px;
                    background: #f0f0f0;
                    margin: 20px 0;
                }
                .question {
                    font-size: 16px;
                    color: #444;
                    margin-bottom: 24px;
                    line-height: 1.5;
                }
                .btn-yes {
                    display: block;
                    width: 100%;
                    padding: 16px;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    border: none;
                    border-radius: 14px;
                    font-size: 17px;
                    font-weight: 600;
                    cursor: pointer;
                    margin-bottom: 12px;
                    transition: opacity 0.2s;
                }
                .btn-yes:disabled { opacity: 0.6; cursor: not-allowed; }
                .btn-no {
                    display: block;
                    width: 100%;
                    padding: 14px;
                    background: #f5f5f5;
                    color: #999;
                    border: none;
                    border-radius: 14px;
                    font-size: 15px;
                    cursor: pointer;
                }
                .hidden { display: none !important; }
                .success-icon { font-size: 70px; margin-bottom: 16px; }
                .success-title { font-size: 22px; color: #2e7d32; margin-bottom: 8px; }
                .success-msg { color: #666; font-size: 15px; line-height: 1.5; }
                .loading { font-size: 40px; animation: spin 1s linear infinite; display: inline-block; }
                @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
            </style>
        </head>
        <body>
        <div class="card">

            <!-- Contact View -->
            <div id="contact-view">
                <div class="avatar">👤</div>
                <div class="company">IoT-Proto</div>
                <h1>{{ name }}</h1>
                <span class="id-badge">ID: {{ item_id }}</span>
                <div class="divider"></div>
                <p class="question">Would you like to contact this person?</p>
                <button class="btn-yes" id="yes-btn" onclick="sendSMS()">
                    📩 Yes, Contact Now
                </button>
                <button class="btn-no" onclick="cancel()">
                    No, Cancel
                </button>
            </div>

            <!-- Loading View -->
            <div id="loading-view" class="hidden">
                <div class="loading">⏳</div>
                <h1 style="margin-top:20px;color:#333">Sending...</h1>
                <p style="color:#666;margin-top:8px">Please wait a moment.</p>
            </div>

            <!-- Success View -->
            <div id="success-view" class="hidden">
                <div class="success-icon">✅</div>
                <h1 class="success-title">Message Sent!</h1>
                <p class="success-msg">
                    The team has been notified.<br>
                    They will reach out shortly.
                </p>
            </div>

            <!-- Cancel View -->
            <div id="cancel-view" class="hidden">
                <div style="font-size:60px;margin-bottom:16px">👋</div>
                <h1 style="color:#333">No problem!</h1>
                <p style="color:#666;margin-top:8px">Have a great day!</p>
            </div>

        </div>

        <script>
            function show(id) {
                ['contact-view','loading-view','success-view','cancel-view']
                    .forEach(v => document.getElementById(v).classList.add('hidden'));
                document.getElementById(id).classList.remove('hidden');
            }

            async function sendSMS() {
                const btn = document.getElementById('yes-btn');
                btn.disabled = true;
                show('loading-view');
                try {
                    const resp = await fetch('/confirm?id={{ item_id }}');
                    if (resp.ok) {
                        show('success-view');
                    } else {
                        alert('Something went wrong. Please try again.');
                        btn.disabled = false;
                        show('contact-view');
                    }
                } catch(e) {
                    alert('Network error. Please try again.');
                    btn.disabled = false;
                    show('contact-view');
                }
            }

            function cancel() {
                show('cancel-view');
            }
        </script>
        </body>
        </html>
        """, name=name, item_id=item_id)

    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/confirm")
def confirm():
    item_id = request.args.get("id")
    if not item_id:
        return "Error", 400

    try:
        response = requests.get(f"{GITHUB_RAW_BASE}/{item_id}.json")
        if response.status_code != 200:
            return "Not found", 404

        data = response.json()
        phone = data.get("phone")

        if phone:
            api_key = os.environ['INFINIREACH_API_KEY']
            numbers = [p.strip() for p in phone.split(',')]
            for p in numbers:
                if not p.startswith('+'):
                    p = '+91' + p
                requests.post(
                    "https://api.infinireach.io/api/v1/messages",
                    headers={
                        "X-API-Key": api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "to": p,
                        "message": "Someone wants to contact you!"
                    }
                )
        return "OK", 200

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)