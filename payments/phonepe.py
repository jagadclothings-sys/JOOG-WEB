import base64
import hashlib
import json
from decimal import Decimal
from typing import Tuple

import requests
from django.conf import settings
from django.urls import reverse


PAY_API_PATH = "/pg/v1/pay"
STATUS_API_PATH_TMPL = "/pg/v1/status/{merchantId}/{merchantTransactionId}"


def _x_verify(path: str, payload_base64: str, salt_key: str, salt_index: str) -> str:
    """Create PhonePe X-VERIFY header value.
    X-VERIFY = SHA256(base64payload + path + salt_key) + "###" + salt_index
    For status API, base64payload is empty string.
    """
    string_to_sign = f"{payload_base64}{path}{salt_key}"
    digest = hashlib.sha256(string_to_sign.encode("utf-8")).hexdigest()
    return f"{digest}###{salt_index}"


def _amount_paise(amount: Decimal) -> int:
    return int((amount or Decimal("0.00")) * 100)


def build_initiate_payload(order, request) -> Tuple[dict, str, str]:
    """Build initiate pay payload and headers.
    Returns (json_payload, base64_payload, x_verify).
    """
    merchant_id = settings.PHONEPE_MERCHANT_ID
    salt_key = settings.PHONEPE_SALT_KEY
    salt_index = str(settings.PHONEPE_SALT_INDEX)

    redirect_url = request.build_absolute_uri(reverse("orders:phonepe_callback"))
    callback_url = redirect_url  # using same endpoint for redirect/callback

    payload = {
        "merchantId": merchant_id,
        "merchantTransactionId": order.phonepe_merchant_txn_id or order.order_number,
        "merchantUserId": str(order.user_id),
        "amount": _amount_paise(order.final_amount),
        "redirectUrl": redirect_url,
        "redirectMode": "POST",
        "callbackUrl": callback_url,
        "paymentInstrument": {
            "type": "PAY_PAGE"
        },
    }

    payload_json = json.dumps(payload, separators=(",", ":"))
    payload_base64 = base64.b64encode(payload_json.encode("utf-8")).decode("utf-8")

    x_verify = _x_verify(PAY_API_PATH, payload_base64, salt_key, salt_index)

    return payload, payload_base64, x_verify


def initiate_payment(order, request) -> dict:
    """Call PhonePe pay API and return response JSON.
    """
    _, payload_base64, x_verify = build_initiate_payload(order, request)

    url = settings.PHONEPE_BASE_URL + PAY_API_PATH
    headers = {
        "Content-Type": "application/json",
        "X-VERIFY": x_verify,
        "X-MERCHANT-ID": settings.PHONEPE_MERCHANT_ID,
    }
    data = {"request": payload_base64}

    resp = requests.post(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


def status_check(merchant_txn_id: str) -> dict:
    """Check transaction status with PhonePe.
    """
    path = STATUS_API_PATH_TMPL.format(
        merchantId=settings.PHONEPE_MERCHANT_ID,
        merchantTransactionId=merchant_txn_id,
    )
    # For status, base64 payload is empty string
    x_verify = _x_verify(path, "", settings.PHONEPE_SALT_KEY, str(settings.PHONEPE_SALT_INDEX))

    url = settings.PHONEPE_BASE_URL + path
    headers = {
        "Content-Type": "application/json",
        "X-VERIFY": x_verify,
        "X-MERCHANT-ID": settings.PHONEPE_MERCHANT_ID,
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()
