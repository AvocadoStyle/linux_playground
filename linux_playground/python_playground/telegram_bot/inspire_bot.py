import os
from time import sleep
import requests
from dotenv import load_dotenv

# Replace with your actual token and chat_id

load_dotenv()
BOT_TOKEN = os.getenv("INSPIRE_BOT_TOKEN")
CHAT_ID = os.getenv("INSPIRE_BOT_CHAT_ID")

def send_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, json=payload)
    return r.json()

# Example usage
if __name__ == "__main__":
    while True:
        msg = 'kaki gadol'
        response = send_message(msg)
        print(response)
        sleep(300)