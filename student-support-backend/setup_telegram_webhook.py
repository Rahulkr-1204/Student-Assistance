#!/usr/bin/env python3
"""
Telegram webhook setup utility.
Prefers a stable deployed backend URL over temporary local tunnel URLs.
"""

import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv


load_dotenv()

CANONICAL_WEBHOOK_PATH = "/api/integrations/telegram/webhook"


def _normalized_base_url():
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


def _build_webhook_url(base_url):
    base = (base_url or "").strip().rstrip("/")
    if not base:
        return ""
    if base.endswith(CANONICAL_WEBHOOK_PATH):
        return base
    return f"{base}{CANONICAL_WEBHOOK_PATH}"


def _secret_token():
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "").strip()
    if not secret or secret == "your_secure_webhook_secret_here":
        return ""
    return secret


def _bot_token():
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


def set_telegram_webhook(webhook_url=None):
    bot_token = _bot_token()
    if not bot_token:
        print("TELEGRAM_BOT_TOKEN not found in .env")
        return False

    resolved_url = webhook_url or _build_webhook_url(_normalized_base_url())
    if not resolved_url:
        print("No webhook URL resolved.")
        print("Set BACKEND_PUBLIC_BASE_URL in .env or pass a full webhook URL.")
        return False

    if not resolved_url.startswith("https://"):
        print("Telegram requires a public HTTPS webhook URL.")
        return False

    print(f"Setting Telegram webhook URL: {resolved_url}")

    try:
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        payload = {
            "url": resolved_url,
            "max_connections": 100,
            "allowed_updates": ["message", "edited_message"],
        }

        secret_token = _secret_token()
        if secret_token:
            payload["secret_token"] = secret_token
            print("Using configured webhook secret")

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data.get("ok"):
            print(f"Failed to set webhook: {data.get('description', 'Unknown error')}")
            return False

        print("Webhook set successfully")
        return check_webhook_info()
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode("utf-8"))
            error_msg = error_data.get("description", str(e))
        except Exception:
            error_msg = str(e)
        print(f"HTTP error: {error_msg}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def delete_webhook():
    bot_token = _bot_token()
    if not bot_token:
        print("TELEGRAM_BOT_TOKEN not found in .env")
        return False

    try:
        url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        req = urllib.request.Request(url, method="POST")
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("ok"):
            print("Webhook deleted successfully")
            return True

        print(f"Failed to delete webhook: {data.get('description', 'Unknown error')}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def check_webhook_info():
    bot_token = _bot_token()
    if not bot_token:
        print("TELEGRAM_BOT_TOKEN not found in .env")
        return False

    try:
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data.get("ok"):
            print("Failed to get webhook info")
            return False

        webhook_info = data.get("result", {})
        print("Current webhook info:")
        print(f"  URL: {webhook_info.get('url', 'Not set')}")
        print(f"  Pending updates: {webhook_info.get('pending_update_count', 0)}")
        if webhook_info.get("last_error_message"):
            print(f"  Last error: {webhook_info['last_error_message']}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    suggested_url = _build_webhook_url(_normalized_base_url())

    print("Telegram Webhook Setup")
    print("=" * 50)
    if suggested_url:
        print(f"Detected deployed webhook URL: {suggested_url}")
    else:
        print("No deployed backend URL detected from environment.")
        print("Set BACKEND_PUBLIC_BASE_URL in .env to your public backend domain.")

    print("1. Set webhook to detected deployed URL")
    print("2. Enter webhook URL manually")
    print("3. Delete webhook")
    print("4. Check webhook info")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        set_telegram_webhook(suggested_url)
        return
    if choice == "2":
        manual_url = input("Enter full HTTPS webhook URL: ").strip()
        set_telegram_webhook(manual_url)
        return
    if choice == "3":
        delete_webhook()
        return
    if choice == "4":
        check_webhook_info()
        return

    print("Invalid choice")


if __name__ == "__main__":
    main()
