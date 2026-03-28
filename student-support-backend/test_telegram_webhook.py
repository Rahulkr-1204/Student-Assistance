#!/usr/bin/env python3
"""
Test the Telegram webhook handler locally with mock data.
"""

import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv


load_dotenv()

LOCAL_WEBHOOK_URL = "http://localhost:5000/api/integrations/telegram/webhook"


def test_telegram_webhook():
    """Test Telegram webhook with mock message data."""
    mock_payload = {
        "message": {
            "chat": {"id": 123456789, "type": "private"},
            "from": {"id": 123456789, "first_name": "Test", "username": "testuser"},
            "text": "Hello, I need help with admissions",
            "date": 1640995200,
        }
    }

    print("Telegram Webhook Local Test")
    print("=" * 50)
    print(f"Mock message: {mock_payload['message']['text']}")

    try:
        req = urllib.request.Request(
            LOCAL_WEBHOOK_URL,
            data=json.dumps(mock_payload).encode("utf-8"),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Webhook-Test", "1")

        secret_token = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
        if secret_token and secret_token != "your_secure_webhook_secret_here":
            req.add_header("X-Telegram-Bot-Api-Secret-Token", secret_token)

        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = json.loads(response.read().decode("utf-8"))

        print("Webhook responded successfully")
        print(json.dumps(response_data, indent=2))

        if response_data.get("ok") and response_data.get("processed", 0) > 0:
            print("Local Telegram webhook test passed")
            return {"status": "success", "response": response_data}

        print("Webhook replied, but the result was incomplete")
        return {"status": "warning", "response": response_data}
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode("utf-8"))
        except Exception:
            error_data = {"error": str(e)}

        print(f"HTTP error {e.code}: {error_data}")
        return {"status": "error", "error": error_data}
    except urllib.error.URLError as e:
        print(f"Connection error: {e}")
        print("Make sure the backend server is running on http://localhost:5000")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"status": "error", "error": str(e)}


def main():
    result = test_telegram_webhook()

    print("\n" + "=" * 50)
    print("Test Result")
    print("=" * 50)
    if result["status"] == "success":
        print("Webhook test passed")
    elif result["status"] == "warning":
        print("Webhook test returned a partial result")
    else:
        print("Webhook test failed")


if __name__ == "__main__":
    main()
