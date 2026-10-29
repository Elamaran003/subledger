import itertools

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db import Base, get_db
from app.main import create_app

_counter = itertools.count(1)


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def client(session_factory):
    app = create_app()

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture()
def make_plan(client):
    def _make(price="100.00", **extra):
        body = {"name": f"plan-{next(_counter)}", "price": price, "currency": "USD", **extra}
        r = client.post("/plans", json=body)
        assert r.status_code == 201, r.text
        return r.json()

    return _make


@pytest.fixture()
def make_customer(client):
    def _make(email=None):
        n = next(_counter)
        r = client.post("/customers", json={"name": f"Cust {n}", "email": email or f"c{n}@example.com"})
        assert r.status_code == 201, r.text
        return r.json()

    return _make


@pytest.fixture()
def subscription(client, make_plan, make_customer):
    """An active subscription on a 100.00 USD plan."""
    plan, customer = make_plan("100.00"), make_customer()
    r = client.post("/subscriptions", json={"customer_id": customer["id"], "plan_id": plan["id"]})
    assert r.status_code == 201, r.text
    return {"subscription": r.json(), "plan": plan, "customer": customer}


@pytest.fixture()
def invoice(client, subscription):
    r = client.post("/invoices/generate", json={"subscription_id": subscription["subscription"]["id"]})
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture()
def pay(client):
    def _pay(invoice_id, amount, status="success", ref=None, currency="USD", **extra):
        return client.post(
            "/payments",
            json={
                "invoice_id": invoice_id,
                "amount": str(amount),
                "currency": currency,
                "status": status,
                "provider_reference": ref or f"ref-{next(_counter)}",
                **extra,
            },
        )

    return _pay
