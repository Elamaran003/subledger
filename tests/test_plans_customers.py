import pytest


@pytest.mark.parametrize("price", ["0", "-5.00"])
def test_plan_price_must_be_greater_than_zero(client, price):
    r = client.post("/plans", json={"name": "Bad", "price": price})
    assert r.status_code == 422


def test_plan_price_update_must_be_greater_than_zero(client, make_plan):
    plan = make_plan("10.00")
    r = client.patch(f"/plans/{plan['id']}", json={"price": "0"})
    assert r.status_code == 422


def test_customer_email_must_be_unique_case_insensitive(client, make_customer):
    make_customer("dup@example.com")
    r = client.post("/customers", json={"name": "Other", "email": "DUP@example.com"})
    assert r.status_code == 409
