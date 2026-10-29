from decimal import Decimal


def test_invoice_amount_due_is_plan_price_snapshot(client, subscription):
    sid, pid = subscription["subscription"]["id"], subscription["plan"]["id"]

    first = client.post(
        "/invoices/generate",
        json={"subscription_id": sid, "period_start": "2026-01-01", "period_end": "2026-02-01"},
    ).json()
    client.patch(f"/plans/{pid}", json={"price": "150.00"})
    second = client.post(
        "/invoices/generate",
        json={"subscription_id": sid, "period_start": "2026-02-01", "period_end": "2026-03-01"},
    ).json()

    assert Decimal(first["amount_due"]) == Decimal("100.00")  # unaffected by later price change
    assert Decimal(second["amount_due"]) == Decimal("150.00")


def test_invoice_defaults_period_and_status(client, invoice):
    assert invoice["status"] == "issued"
    assert Decimal(invoice["amount_paid"]) == 0
    assert invoice["period_end"] > invoice["period_start"]


def test_cannot_invoice_cancelled_subscription(client, subscription):
    sid = subscription["subscription"]["id"]
    client.post(f"/subscriptions/{sid}/cancel")
    assert client.post("/invoices/generate", json={"subscription_id": sid}).status_code == 422


def test_duplicate_period_invoice_rejected(client, subscription):
    body = {
        "subscription_id": subscription["subscription"]["id"],
        "period_start": "2026-01-01",
        "period_end": "2026-02-01",
    }
    assert client.post("/invoices/generate", json=body).status_code == 201
    assert client.post("/invoices/generate", json=body).status_code == 409


def test_invoice_for_unknown_subscription_404(client):
    assert client.post("/invoices/generate", json={"subscription_id": 999}).status_code == 404
