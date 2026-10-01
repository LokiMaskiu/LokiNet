from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory
import json
import os
import requests

app = Flask(__name__)
app.secret_key = "SABIT_SECRET_KEY_12345"

GEMINI_API_KEY = "AQ.Ab8RN6L6w7XIs033luDUU2XIgXl9Gp9bbzdLHFjGmLCzC9pvIg"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
CHAT_FILE = os.path.join(BASE_DIR, "chats.json")

# -------------------------
# FAVICON ROUTE (KESİN ÇÖZÜM)
# -------------------------
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

# -------------------------
# SAFE LOAD
# -------------------------
def load():
    global users, chats

    users = {}
    chats = {}

    if os.path.exists(USERS_FILE):
        try:
            users = json.load(open(USERS_FILE, "r"))
        except:
            users = {}

    if os.path.exists(CHAT_FILE):
        try:
            chats = json.load(open(CHAT_FILE, "r"))
        except:
            chats = {}

def save():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

    with open(CHAT_FILE, "w") as f:
        json.dump(chats, f, indent=4)

load()

# -------------------------
# GEMINI AI
# -------------------------
def gemini(text):

    system_prompt = """
Sen LokiAI isimli bir yapay zeka asistanısın.

Kurallar:
- Adın LokiAI'dir.
- Kendini Gemini veya Google AI olarak tanıtma.
- "Sen kimsin?" sorusuna "Ben LokiAI'yim." diye cevap ver.
- "Adın ne?" sorusuna "Ben LokiAI'yim." diye cevap ver.
- "Geliştiricin kim?" sorusuna "Ben LokiMaskiu tarafından geliştirilen LokiAI'yim." diye cevap ver.
"""

    prompt = f"{system_prompt}\n\nKullanıcı: {text}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        r = requests.post(url, json=payload, timeout=20)
        data = r.json()

        if "error" in data:
            return "API HATA: " + data["error"]["message"]

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return str(e)

# -------------------------
# HOME
# -------------------------
@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"))

# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    hata = None

    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        if not u or not p:
            hata = "Boş alan bırakma"

        elif u in users:
            hata = "Kullanıcı var"

        else:
            users[u] = p
            save()
            return redirect("/login")

    return render_template("register.html", hata=hata)

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    hata = None

    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        if not u or not p:
            hata = "Boş alan bırakma"

        elif u not in users:
            hata = "Kullanıcı bulunamadı"

        elif users[u] != p:
            hata = "Şifre yanlış"

        else:
            session["user"] = u
            return redirect("/panel")

    return render_template("login.html", hata=hata)

# -------------------------
# PANEL
# -------------------------
@app.route("/panel")
def panel():
    if "user" not in session:
        return redirect("/login")

    return render_template("panel.html", user=session["user"], chat=chats.get(session["user"], []))

# -------------------------
# CHAT
# -------------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"error": "not logged"}), 401

    u = session["user"]
    msg = request.json.get("soru", "")

    chats.setdefault(u, []).append({"sender": "user", "text": msg})

    msg_lower = msg.lower()

    if "sen kimsin" in msg_lower:
        reply = "Ben LokiAI'yim."

    elif "adın ne" in msg_lower:
        reply = "Ben LokiAI'yim."

    elif "geliştiricin kim" in msg_lower:
        reply = "Ben LokiMaskiu tarafından geliştirilen LokiAI'yim."

    else:
        reply = gemini(msg)

        chats[u].append({"sender": "ai", "text": reply})

        save()

    return jsonify({"cevap": reply})

# -------------------------
# DELETE
# -------------------------
@app.route("/delete")
def delete():
    if "user" not in session:
        return redirect("/login")

    u = session["user"]

    users.pop(u, None)
    chats.pop(u, None)

    save()
    session.clear()

    return redirect("/")

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)