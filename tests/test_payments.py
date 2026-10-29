from decimal import Decimal


def test_partial_payment_moves_invoice_to_partially_paid(client, invoice, pay):
    r = pay(invoice["id"], "40.00")
    assert r.status_code == 201
    inv = r.json()["invoice"]
    assert inv["status"] == "partially_paid"
    assert Decimal(inv["amount_paid"]) == Decimal("40.00")
    assert Decimal(inv["amount_remaining"]) == Decimal("60.00")


def test_full_payment_moves_invoice_to_paid(client, invoice, pay):
    assert pay(invoice["id"], "40.00").status_code == 201
    r = pay(invoice["id"], "60.00")
    assert r.json()["invoice"]["status"] == "paid"
    assert Decimal(r.json()["invoice"]["amount_remaining"]) == 0


def test_payment_cannot_exceed_remaining_amount(client, invoice, pay):
    pay(invoice["id"], "90.00")
    r = pay(invoice["id"], "10.01")
    assert r.status_code == 422
    # nothing changed
    assert Decimal(client.get(f"/invoices/{invoice['id']}").json()["amount_paid"]) == Decimal("90.00")


def test_failed_payment_does_not_increase_amount_paid(client, invoice, pay):
    r = pay(invoice["id"], "100.00", status="failed", failure_reason="card_declined")
    assert r.status_code == 201
    body = r.json()
    assert body["payment_attempt"]["status"] == "failed"
    assert body["payment_attempt"]["failure_reason"] == "card_declined"
    assert Decimal(body["invoice"]["amount_paid"]) == 0
    assert body["invoice"]["status"] == "issued"


def test_failed_payment_then_retry_succeeds(client, invoice, pay):
    pay(invoice["id"], "100.00", status="failed")
    r = pay(invoice["id"], "100.00")
    assert r.json()["invoice"]["status"] == "paid"
    assert len(client.get(f"/invoices/{invoice['id']}/payments").json()) == 2


def test_duplicate_provider_reference_rejected(client, invoice, pay):
    assert pay(invoice["id"], "10.00", ref="abc").status_code == 201
    assert pay(invoice["id"], "10.00", ref="abc").status_code == 409


def test_currency_mismatch_rejected(client, invoice, pay):
    assert pay(invoice["id"], "10.00", currency="EUR").status_code == 422


def test_paid_invoice_rejects_further_payments(client, invoice, pay):
    pay(invoice["id"], "100.00")
    assert pay(invoice["id"], "1.00").status_code == 422


def test_zero_or_negative_payment_rejected(client, invoice, pay):
    assert pay(invoice["id"], "0").status_code == 422
    assert pay(invoice["id"], "-1").status_code == 422
