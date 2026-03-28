#!/usr/bin/env python3
"""
Telegram integration verification script.
Checks bot credentials against Telegram and verifies the local webhook handler.
"""

import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv


load_dotenv()

LOCAL_WEBHOOK_URL = "http://localhost:5000/api/integrations/telegram/webhook"


def test_telegram_bot():
    """Test Telegram bot token validity."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")

    if not bot_token:
        return {"status": "error", "message": "TELEGRAM_BOT_TOKEN not found in .env"}

    print("[1/2] Testing Telegram bot token...")
    print(f"Token prefix: {bot_token[:20]}...")

    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("ok"):
            bot_info = data.get("result", {})
            print("Bot authentication successful")
            print(f"Bot name: {bot_info.get('first_name', 'Unknown')}")
            print(f"Username: @{bot_info.get('username', 'Unknown')}")
            print(f"Bot ID: {bot_info.get('id', 'Unknown')}")
            return {
                "status": "success",
                "bot_info": bot_info,
                "message": "Telegram bot token is valid and authenticated",
            }

        error_description = data.get("description", "Unknown error")
        print(f"Bot authentication failed: {error_description}")
        return {
            "status": "error",
            "message": f"Telegram API error: {error_description}",
        }
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode("utf-8"))
            error_msg = error_data.get("description", str(e))
        except Exception:
            error_msg = str(e)

        print(f"HTTP error: {error_msg}")
        return {"status": "error", "message": f"HTTP error: {error_msg}"}
    except Exception as e:
        print(f"Connection error: {e}")
        return {"status": "error", "message": f"Connection error: {e}"}


def test_webhook_endpoint():
    """Test the local webhook handler with a mock Telegram update."""
    print("\n[2/2] Testing local Telegram webhook handler...")

    payload = {
        "message": {
            "chat": {"id": 123456789, "type": "private"},
            "from": {"id": 123456789, "first_name": "Test", "username": "testuser"},
            "text": "Hello",
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

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("ok"):
            print("Webhook handler is reachable and processed the mock update")
            print(f"Preview reply: {data.get('reply_preview', '')}")
            return {"status": "success", "message": "Webhook endpoint accessible"}

        print("Webhook handler returned an unexpected response")
        return {"status": "error", "message": "Unexpected webhook response"}
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("Webhook endpoint reached, but webhook secret is invalid or missing")
            return {"status": "warning", "message": "Webhook secret invalid or missing"}

        print(f"Webhook endpoint error: HTTP {e.code}")
        return {"status": "error", "message": f"HTTP {e.code}"}
    except Exception as e:
        print(f"Cannot connect to local webhook: {e}")
        print("Make sure the backend server is running on http://localhost:5000")
        return {"status": "error", "message": "Backend server not running"}


def main():
    print("Telegram Integration Verification")
    print("=" * 50)

    bot_result = test_telegram_bot()
    webhook_result = test_webhook_endpoint()

    print("\n" + "=" * 50)
    print("Verification Summary")
    print("=" * 50)

    if bot_result["status"] == "success":
        print("Telegram bot token: VALID")
        print(
            f"Bot: {bot_result['bot_info'].get('first_name')} "
            f"(@{bot_result['bot_info'].get('username')})"
        )
    else:
        print("Telegram bot token: INVALID")
        print(f"Error: {bot_result['message']}")

    if webhook_result["status"] == "success":
        print("Webhook handler: ACCESSIBLE")
    elif webhook_result["status"] == "warning":
        print("Webhook handler: SECRET MISMATCH")
    else:
        print("Webhook handler: NOT ACCESSIBLE")

    print("\nNext steps:")
    print("1. Run the backend locally before testing the webhook handler")
    print("2. Set Telegram webhook to a public HTTPS URL that ends with /api/integrations/telegram/webhook")
    print("3. Use the same TELEGRAM_WEBHOOK_SECRET value when calling setWebhook")


if __name__ == "__main__":
    main()
