#!/usr/bin/env python3
"""
Quick Telegram webhook setup helper.
Uses one canonical webhook path: /api/integrations/telegram/webhook
"""

import json
import os
import urllib.request

from dotenv import load_dotenv


load_dotenv()

CANONICAL_WEBHOOK_PATH = "/api/integrations/telegram/webhook"
LOCAL_WEBHOOK_URL = f"http://localhost:5000{CANONICAL_WEBHOOK_PATH}"


def _public_base_url():
    candidates = [
        os.getenv("BACKEND_PUBLIC_BASE_URL", "").strip(),
        os.getenv("RENDER_EXTERNAL_URL", "").strip(),
        os.getenv("RAILWAY_STATIC_URL", "").strip(),
    ]

    railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if railway_public_domain:
        candidates.append(f"https://{railway_public_domain}")

    for candidate in candidates:
        if candidate:
            return candidate.rstrip("/")

    return ""


def set_webhook(webhook_url):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        print("TELEGRAM_BOT_TOKEN not found in .env")
        return False

    try:
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        payload = {
            "url": webhook_url,
            "max_connections": 100,
            "allowed_updates": ["message", "edited_message"],
        }

        secret_token = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
        if secret_token and secret_token != "your_secure_webhook_secret_here":
            payload["secret_token"] = secret_token
            print("Using configured webhook secret")

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")

        print(f"Setting Telegram webhook to: {webhook_url}")
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data.get("ok"):
            print(f"Failed to set webhook: {data.get('description', 'Unknown error')}")
            return False

        print("Webhook set successfully")
        info_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        with urllib.request.urlopen(info_url, timeout=10) as info_response:
            info_data = json.loads(info_response.read().decode("utf-8"))

        if info_data.get("ok"):
            webhook_info = info_data.get("result", {})
            print(f"Telegram webhook URL: {webhook_info.get('url', 'Not set')}")
            print(f"Pending updates: {webhook_info.get('pending_update_count', 0)}")
            if webhook_info.get("last_error_message"):
                print(f"Last Telegram error: {webhook_info['last_error_message']}")

        return True
    except Exception as e:
        print(f"Error while setting webhook: {e}")
        return False


def test_local_handler():
    print("\nTesting local webhook handler with mock data...")
    payload = {
        "message": {
            "chat": {"id": 123456789, "type": "private"},
            "from": {"id": 123456789, "first_name": "Test", "username": "testuser"},
            "text": "Hello! I need help with admissions",
        }
    }

    try:
        req = urllib.request.Request(
            LOCAL_WEBHOOK_URL,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Webhook-Test", "1")

        secret_token = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
        if secret_token and secret_token != "your_secure_webhook_secret_here":
            req.add_header("X-Telegram-Bot-Api-Secret-Token", secret_token)

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("ok"):
            print("Local Telegram handler works")
            print(f"Reply preview: {data.get('reply_preview', '')}")
            return True

        print("Local Telegram handler returned an unexpected response")
        return False
    except Exception as e:
        print(f"Local webhook test failed: {e}")
        print("Make sure your backend server is running on http://localhost:5000")
        return False


def main():
    detected_base_url = _public_base_url()

    print("Quick Telegram Webhook Setup")
    print("=" * 50)
    if detected_base_url:
        print(f"Detected public backend URL: {detected_base_url}")
    else:
        print("No public backend URL detected from environment.")
        print("Set BACKEND_PUBLIC_BASE_URL in .env for stable deployed webhook setup.")

    print("1. Set webhook using detected deployed backend URL")
    print("2. Enter a public HTTPS base URL manually")
    print("3. Test local webhook handler only")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        if not detected_base_url:
            print("No deployed backend URL detected. Set BACKEND_PUBLIC_BASE_URL first.")
            return
        webhook_url = f"{detected_base_url}{CANONICAL_WEBHOOK_PATH}"
        if set_webhook(webhook_url):
            print("\nNext steps:")
            print("1. Redeploy your backend if you changed code or environment variables")
            print("2. Send a message to your Telegram bot")
            print("3. Check Telegram webhook info if delivery still fails")
        return

    if choice == "2":
        base_url = input("Enter your public HTTPS base URL (for example, https://abc123.ngrok-free.app): ").strip().rstrip("/")
        if not base_url.startswith("https://"):
            print("Telegram requires a public HTTPS URL.")
            return

        webhook_url = f"{base_url}{CANONICAL_WEBHOOK_PATH}"
        if set_webhook(webhook_url):
            print("\nNext steps:")
            print("1. Keep your backend running and reachable at that public URL")
            print("2. Send a message to your Telegram bot")
            print("3. Check backend logs if delivery still fails")
        return

    if choice == "3":
        test_local_handler()
        return

    print("Invalid choice")


if __name__ == "__main__":
    main()
