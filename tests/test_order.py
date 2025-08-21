import datetime
import pytest


@pytest.mark.anyio
async def test_add_order(client, make_pets):
    data = {"quantity": 4, "petId": make_pets[0].id}
    post_res = client.post("/api/v3/orders", json=data)
    assert post_res.status_code == 201
    assert post_res.json()["quantity"] == 4
    assert post_res.json()["petId"] == make_pets[0].id
    assert post_res.json()["status"] == "placed"


@pytest.mark.anyio
async def test_add_order_validations(client, make_pets):
    data = {"quantity": 4}
    post_res = client.post("/api/v3/orders", json=data)
    assert post_res.status_code == 400
    assert "required property" in post_res.json()["detail"]

    data["petId"] = 0
    post_res = client.post("/api/v3/orders", json=data)
    assert post_res.status_code == 400
    assert "Invalid petId" in str(post_res.json()["detail"])

    data = {"petId": make_pets[0].id, "quantity": 4, "shipDate": "77777-jj-8888"}
    post_res = client.post("/api/v3/orders", json=data)
    assert post_res.status_code == 400
    assert "Invalid date format" in str(post_res.json()["detail"])


@pytest.mark.anyio
async def test_get_order_by_id(client, make_orders):
    order_id = make_orders[0].id
    get_res = client.get(f"/api/v3/orders/{order_id}")
    assert get_res.status_code == 200
    assert get_res.json()["quantity"] == 4
    assert get_res.json()["status"] == make_orders[0].status

    get_res = client.get(f"/api/v3/orders/0")
    assert get_res.status_code == 404
    assert "Order not found" in str(get_res.json()["detail"])


@pytest.mark.anyio
async def test_update_order(client, make_orders):
    order_id = make_orders[0].id
    shipDate = make_orders[0].shipDate + datetime.timedelta(days=7)
    shipDate = shipDate.strftime("%Y-%m-%d")
    data = {"status": "approved", "quantity": 2, "shipDate": shipDate}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert put_res.status_code == 200
    assert put_res.json()["status"] == data["status"]
    assert put_res.json()["quantity"] == data["quantity"]
    assert put_res.json()["shipDate"] == data["shipDate"]

    # Confirm
    get_res = client.get(f"/api/v3/orders/{order_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == data["status"]
    assert get_res.json()["quantity"] == data["quantity"]
    assert put_res.json()["shipDate"] == data["shipDate"]


@pytest.mark.anyio
async def test_update_order_validations(client, make_orders):
    order_id = make_orders[0].id
    data = {"shipDate": "77777-jj-8888"}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert put_res.status_code == 400
    assert "Invalid date format" in str(put_res.json()["detail"])

    data = {"petId": 0}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert put_res.status_code == 400
    assert "Invalid petId" in put_res.json()["detail"]


@pytest.mark.anyio
async def test_get_orders(client, make_orders):
    get_res = client.get(f"/api/v3/orders/")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 2


@pytest.mark.anyio
async def test_get_orders_by_petid(client, make_orders):
    params = {"petId": make_orders[0].petId}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["quantity"] == make_orders[0].quantity


@pytest.mark.anyio
async def test_get_orders_by_status(client, make_orders):
    params = {"status": make_orders[0].status}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["quantity"] == make_orders[0].status

    params = {"status": "approvedxx"}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 0


@pytest.mark.anyio
async def test_delete_order(client, make_orders):
    order_id = make_orders[0].id
    del_res = client.delete(f"/api/v3/orders/{order_id}")
    assert del_res.status_code == 204

    # Confirm
    check = client.get(f"/api/v3/orders/{order_id}")
    assert check.status_code == 404
