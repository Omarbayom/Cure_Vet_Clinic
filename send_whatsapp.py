# send_whatsapp.py
import os
import requests

PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
ACCESS_TOKEN    = os.getenv("WHATSAPP_ACCESS_TOKEN")

def send_whatsapp_message(to: str, body: str) -> dict:
    """
    Send a WhatsApp text message via the Cloud API.
    - to: recipient in E.164 format (e.g. "+201012345678")
    - body: the message text

    Returns the API’s JSON response or raises on error.
    """
    if not PHONE_NUMBER_ID or not ACCESS_TOKEN:
        raise RuntimeError("WhatsApp credentials not set in env vars")
        
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": { "body": body }
    }
    
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()
