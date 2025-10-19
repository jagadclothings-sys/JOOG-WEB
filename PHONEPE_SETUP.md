# PhonePe Payment Gateway Integration

This project is configured to use PhonePe (PG) instead of Stripe.

1) Environment variables (add to .env or production env)

- PHONEPE_MERCHANT_ID=your-merchant-id
- PHONEPE_SALT_KEY=your-salt-key
- PHONEPE_SALT_INDEX=1
- PHONEPE_ENV=SANDBOX  # or PRODUCTION
- PHONEPE_BASE_URL     # optional; auto-selected by env if not set

2) How it works

- After checkout, user lands on /orders/payment/<order_number>/
- "Pay with PhonePe" button calls /orders/pay/phonepe/initiate/<order_number>/
- Server builds signed payload and calls POST {BASE}/pg/v1/pay
- User is redirected to PhonePe hosted page
- PhonePe redirects back to /orders/pay/phonepe/callback/
- Server verifies transaction via GET {BASE}/pg/v1/status/{merchantId}/{merchantTransactionId}
- On success: order is confirmed, stock reduced, emails sent

3) Test (Sandbox)

- Set PHONEPE_ENV=SANDBOX
- PHONEPE_BASE_URL defaults to https://api-preprod.phonepe.com/apis/pg-sandbox
- Use the test credentials from your PhonePe dashboard

4) Code touchpoints

- settings: PHONEPE_* variables
- Model changes: Order now stores phonepe_merchant_txn_id, phonepe_txn_id, phonepe_meta
- Utils: payments/phonepe.py (signing and API calls)
- Views/URLs: orders.views.phonepe_initiate and phonepe_callback; URLs under /orders/pay/phonepe/
- Template: templates/orders/payment.html shows the PhonePe button

5) Notes

- Amount is sent as paise (INR * 100)
- X-VERIFY uses SHA256(base64payload + path + salt_key) + "###" + salt_index
- Status is verified server-to-server before confirming the order
- Ensure your domain is configured in PhonePe dashboard for redirect/callback URLs
