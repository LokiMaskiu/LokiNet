import requests

API_KEY = "AQ.Ab8RN6L6w7XIs033luDUU2XIgXl9Gp9bbzdLHFjGmLCzC9pvIg"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

payload = {
    "contents": [
        {
            "parts": [{"text": "hello"}]
        }
    ]
}

r = requests.post(url, json=payload)

print("STATUS:", r.status_code)
print("RAW:", r.text)