import os
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CSV_FILE = "submissions.csv"

# Fixed Redirect URL jo aapne manga hai
TARGET_REDIRECT_URL = "http://127.0.0.1:5000"

# Initialize CSV file with headers if missing
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Username", "Referral_Key", "User_Profile_Link", "IP_Address"])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/submit", methods=["POST"])
def handle_submit():
    if request.is_json:
        data = request.get_json(silent=True) or {}
        username = data.get("username", "")
        referral_key = data.get("referral_key", "")
        profile_link = data.get("profile_link", "")
    else:
        username = request.form.get("username", "")
        referral_key = request.form.get("referral_key", "")
        profile_link = request.form.get("profile_link", "")

    username = str(username).strip().lstrip("@")
    referral_key = str(referral_key).strip()
    profile_link = str(profile_link).strip()

    # Strict Validation: Sabhi fields compulsory hain
    if not username or not referral_key or not profile_link:
        msg = "Error: Sabhi fields (Username, Email, Profile Link) bharna anivarya hai!"
        if request.is_json:
            return jsonify({"success": False, "message": msg}), 400
        return msg, 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # 1. LIVE TERMINAL PRINT
    print("\n" + "=" * 55, flush=True)
    print(" 🚀 [NEW USER DATA SAVED & REDIRECTING TO COLLABSTR]", flush=True)
    print("=" * 55, flush=True)
    print(f" 👤 Username      : @{username}", flush=True)
    print(f" 🔑 Email : {referral_key}", flush=True)
    print(f" 🔗 Profile Link  : {profile_link}", flush=True)
    print(f" 🌐 IP Address    : {client_ip}", flush=True)
    print(f" 🕒 Timestamp     : {timestamp}", flush=True)
    print("=" * 55 + "\n", flush=True)

    # 2. SAVE DATA TO CSV
    try:
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, username, referral_key, profile_link, client_ip])
    except Exception as e:
        print(f"❌ CSV Write Error: {e}", flush=True)

    # 3. Response handling: Data save karke Collabstr par redirect karega
    if request.is_json:
        return jsonify({
            "success": True,
            "message": "Data collected successfully!",
            "redirect_url": TARGET_REDIRECT_URL
        }), 200
    else:
        return redirect(TARGET_REDIRECT_URL)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n⚡ Server running at http://127.0.0.1:{port}\n", flush=True)
    app.run(host="0.0.0.0", port=port, debug=True)
