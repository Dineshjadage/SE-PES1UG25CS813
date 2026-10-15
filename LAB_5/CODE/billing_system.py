
"""Subscription billing demonstration with security checks."""

import calendar
import hashlib
import hmac
import os
import secrets
from datetime import date
from html import escape

from lxml import etree
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


PLANS = {"basic": 199, "pro": 499, "team": 999}
GST = 0.18
TRIAL_DAYS = 14
MAX_ATTEMPTS = 3

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
CARD_KEY_HEX = os.environ.get("CARD_ENCRYPTION_KEY", "")

subscriptions = {}
coupons = {
    "WELCOME10": {"percent": 10, "expires": date(2026, 12, 31)},
    "FRIENDS150": {"percent": 150, "expires": date(2027, 1, 31)},
}


def subscribe(user, plan, start):
    """Create a subscription for a valid plan."""
    if plan not in PLANS:
        raise ValueError("Unknown subscription plan")

    subscriptions[user] = {
        "plan": plan,
        "start": start,
        "status": "trial",
        "invoices": [],
    }
    return subscriptions[user]


def is_trial_over(user, today):
    """Check whether a subscription trial has ended."""
    if user not in subscriptions:
        raise ValueError("Unknown user")

    elapsed_days = (today - subscriptions[user]["start"]).days
    return elapsed_days >= TRIAL_DAYS


def apply_coupon(amount, code, today):
    """Apply a valid coupon without allowing negative invoice totals."""
    if amount < 0:
        raise ValueError("Amount cannot be negative")

    coupon = coupons.get(code)
    if coupon is None or today >= coupon["expires"]:
        return amount

    percent = coupon["percent"]
    if not 0 <= percent <= 100:
        return amount

    return max(0, amount - amount * percent / 100)


def invoice_amount(user, code=None, today=None):
    """Calculate the subscription invoice including tax."""
    if user not in subscriptions:
        raise ValueError("Unknown user")

    if today is None:
        today = date.today()

    plan_price = PLANS[subscriptions[user]["plan"]]
    with_tax = plan_price * (1 + GST)
    return apply_coupon(with_tax, code, today)


def next_billing_date(current):
    """Advance one calendar month, handling month-end dates."""
    if current.month == 12:
        year = current.year + 1
        month = 1
    else:
        year = current.year
        month = current.month + 1

    last_day = calendar.monthrange(year, month)[1]
    return current.replace(
        year=year,
        month=month,
        day=min(current.day, last_day),
    )


def prorate_upgrade(user, new_plan, today, period_end):
    """Calculate the prorated cost of a plan upgrade."""
    if user not in subscriptions:
        raise ValueError("Unknown user")
    if new_plan not in PLANS:
        raise ValueError("Unknown subscription plan")

    days_left = (period_end - today).days
    if days_left < 0:
        raise ValueError("Period end cannot precede today")

    old_price = PLANS[subscriptions[user]["plan"]]
    new_price = PLANS[new_plan]
    subscriptions[user]["plan"] = new_plan

    return max(0, (new_price - old_price) * days_left / 30)


def retry_payment(charge):
    """Attempt payment no more than MAX_ATTEMPTS times."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        if charge():
            return attempt
    return MAX_ATTEMPTS


def cancel_refund(user, days_used):
    """Refund the unused portion of a 30-day billing period."""
    if user not in subscriptions:
        raise ValueError("Unknown user")
    if not 0 <= days_used <= 30:
        raise ValueError("Days used must be between 0 and 30")

    price = PLANS[subscriptions[user]["plan"]]
    return price * (30 - days_used) / 30


def coupon_code():
    """Generate a coupon using a cryptographically secure random source."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    suffix = "".join(secrets.choice(alphabet) for _ in range(6))
    return f"SAVE-{suffix}"


def active_users():
    """Return users without any invoices."""
    return {
        user
        for user, subscription in subscriptions.items()
        if not subscription["invoices"]
    }


def encrypt_card(card_number):
    """Encrypt card data using AES-GCM and a configured 256-bit key."""
    if len(CARD_KEY_HEX) != 64:
        raise RuntimeError(
            "Set CARD_ENCRYPTION_KEY to a 64-character hexadecimal key"
        )

    try:
        key = bytes.fromhex(CARD_KEY_HEX)
    except ValueError as exc:
        raise ValueError(
            "CARD_ENCRYPTION_KEY must be hexadecimal"
        ) from exc

    nonce = secrets.token_bytes(12)
    cipher = AESGCM(key)
    ciphertext = cipher.encrypt(
        nonce,
        card_number.encode("utf-8"),
        None,
    )
    return (nonce + ciphertext).hex()


def verify_webhook(body, signature):
    """Verify a webhook HMAC using the configured secret."""
    if not WEBHOOK_SECRET:
        raise RuntimeError("Set the WEBHOOK_SECRET environment variable")

    expected = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_webhook(xml_bytes):
    """Parse webhook XML without resolving external entities."""
    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
    )
    root = etree.fromstring(xml_bytes, parser=parser)

    return {
        "event": root.findtext("event"),
        "user": root.findtext("user"),
    }


def render_invoice(user, amount):
    """Render an invoice with escaped user input."""
    if amount < 0:
        raise ValueError("Invoice amount cannot be negative")

    safe_user = escape(str(user))
    return (
        f"<h1>Invoice for {safe_user}</h1>"
        f"<p>Total: Rs.{amount}</p>"
    )


def main():
    """Run the subscription billing demonstration."""
    subscribe("asha", "pro", date(2026, 9, 1))
    subscribe(
        "<b onmouseover=alert(1)>ravi</b>",
        "basic",
        date(2026, 9, 20),
    )

    print(
        "Trial over on 09-15?",
        is_trial_over("asha", date(2026, 9, 15)),
    )
    print(
        "Pro invoice with WELCOME10:",
        invoice_amount("asha", "WELCOME10", date(2026, 10, 1)),
    )
    print(
        "Pro invoice with FRIENDS150:",
        invoice_amount("asha", "FRIENDS150", date(2026, 10, 1)),
    )
    print(
        "Coupon on its expiry day:",
        invoice_amount("asha", "WELCOME10", date(2026, 12, 31)),
    )
    print(
        "Next billing after 2026-10-15:",
        next_billing_date(date(2026, 10, 15)),
    )
    print(
        "Upgrade pro->team with 10 days left:",
        prorate_upgrade(
            "asha",
            "team",
            date(2027, 2, 18),
            date(2027, 2, 28),
        ),
    )

    calls = []
    print(
        "Payment attempts (maximum 3):",
        retry_payment(lambda: calls.append(1) and False),
    )
    print(
        "Refund after 25 of 30 days:",
        cancel_refund("asha", 25),
    )

    if len(CARD_KEY_HEX) == 64:
        first = encrypt_card("4111111111111111")
        second = encrypt_card("4111111111111111")
        print("Same card, same ciphertext?", first == second)
    else:
        print("Card encryption demo skipped: configure CARD_ENCRYPTION_KEY")

    if WEBHOOK_SECRET:
        signature = hmac.new(
            WEBHOOK_SECRET.encode("utf-8"),
            b"<x/>",
            hashlib.sha256,
        ).hexdigest()
        print(
            "Webhook verified:",
            verify_webhook(b"<x/>", signature),
        )
    else:
        print("Webhook demo skipped: configure WEBHOOK_SECRET")

    print(
        "Webhook:",
        parse_webhook(
            b"<hook><event>paid</event><user>asha</user></hook>"
        ),
    )
    print(
        "Invoice HTML:",
        render_invoice("<b onmouseover=alert(1)>ravi</b>", 199),
    )
    print("Coupon:", coupon_code())


if __name__ == "__main__":
    main()
