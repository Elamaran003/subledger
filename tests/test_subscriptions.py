def test_cannot_subscribe_to_inactive_plan(client, make_plan, make_customer):
    plan, customer = make_plan(), make_customer()
    client.post(f"/plans/{plan['id']}/deactivate")
    r = client.post("/subscriptions", json={"customer_id": customer["id"], "plan_id": plan["id"]})
    assert r.status_code == 422


def test_no_two_active_subscriptions_to_same_plan(client, subscription):
    r = client.post(
        "/subscriptions",
        json={"customer_id": subscription["customer"]["id"], "plan_id": subscription["plan"]["id"]},
    )
    assert r.status_code == 409


def test_can_resubscribe_after_cancelling(client, subscription):
    sid = subscription["subscription"]["id"]
    assert client.post(f"/subscriptions/{sid}/cancel").status_code == 200
    r = client.post(
        "/subscriptions",
        json={"customer_id": subscription["customer"]["id"], "plan_id": subscription["plan"]["id"]},
    )
    assert r.status_code == 201


def test_different_customers_can_share_a_plan(client, subscription, make_customer):
    other = make_customer()
    r = client.post("/subscriptions", json={"customer_id": other["id"], "plan_id": subscription["plan"]["id"]})
    assert r.status_code == 201
