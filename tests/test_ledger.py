import pytest

from app.exceptions import LedgerImmutableError
from app.models import LedgerEntry


def test_invoice_and_payments_create_traceable_ledger_entries(client, invoice, pay):
    p1 = pay(invoice["id"], "30.00").json()["payment_attempt"]
    p2 = pay(invoice["id"], "10.00", status="failed", failure_reason="insufficient_funds").json()["payment_attempt"]

    entries = client.get("/ledger", params={"invoice_id": invoice["id"]}).json()
    assert [e["entry_type"] for e in entries] == ["invoice_created", "payment_success", "payment_failure"]

    by_ref = lambda ref: client.get("/ledger", params={"reference_id": ref}).json()
    assert len(by_ref(f"invoice:{invoice['id']}")) == 1
    assert by_ref(f"payment:{p1['id']}")[0]["entry_type"] == "payment_success"
    assert by_ref(f"payment:{p2['id']}")[0]["entry_type"] == "payment_failure"


def test_rejected_payment_writes_no_ledger_entry(client, invoice, pay):
    pay(invoice["id"], "500.00")  # overpayment -> 422
    entries = client.get("/ledger", params={"invoice_id": invoice["id"]}).json()
    assert [e["entry_type"] for e in entries] == ["invoice_created"]


def test_ledger_entries_are_append_only(client, invoice, session_factory):
    db = session_factory()
    entry = db.query(LedgerEntry).first()

    entry.description = "tampered"
    with pytest.raises(LedgerImmutableError):
        db.commit()
    db.rollback()

    db.delete(db.query(LedgerEntry).first())
    with pytest.raises(LedgerImmutableError):
        db.commit()
    db.rollback()
    db.close()
