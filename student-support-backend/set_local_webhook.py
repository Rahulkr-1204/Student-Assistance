#!/usr/bin/env python3
"""
Deprecated helper kept as a guardrail.
Telegram cannot deliver webhook events to localhost directly.
"""


def main():
    print("Telegram cannot use localhost as a real webhook target.")
    print("Use a public HTTPS URL that ends with /api/integrations/telegram/webhook.")
    print("For local development, start the backend and use ngrok or another HTTPS tunnel.")


if __name__ == "__main__":
    main()
