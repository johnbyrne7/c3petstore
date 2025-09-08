import datetime
import pytest


@pytest.mark.anyio
async def test_add_order(client, make_pets):
    petIds = [{"quantity": 4, "petId": make_pets[0].id}]
    data = {"petIds": petIds}
    post_res = client.post("/api/v3/orders", json=data)
    assert post_res.status_code == 201
    assert post_res.json()["status"] == "placed"
    assert post_res.json()["petIds"][0]["quantity"] == 4
    assert post_res.json()["petIds"][0]["petId"] == make_pets[0].id


@pytest.mark.anyio
async def test_add_order_validations(client, make_pets):
    post_res = client.post("/api/v3/orders", json={})
    assert post_res.status_code == 400
    assert "is a required property" in str(post_res.json()["detail"])

    petIds = [{"quantity": 4}]
    data = {"petIds": petIds}
    post_res = client.post("/api/v3/orders", json=data)
    assert post_res.status_code == 400
    assert "is a required property" in str(post_res.json()["detail"])

    petIds[0]["petId"] = 0
    post_res = client.post("/api/v3/orders", json=data)
    assert post_res.status_code == 400
    assert "Invalid petId" in str(post_res.json()["detail"])

    petIds[0]["petId"] = make_pets[0].id
    data["shipDate"] = "77777-jj-8888"
    post_res = client.post("/api/v3/orders", json=data)
    assert post_res.status_code == 400
    assert "Invalid date format" in str(post_res.json()["detail"])


@pytest.mark.anyio
async def test_get_order_by_id(client, make_orders):
    order_id = make_orders[0].id
    get_res = client.get(f"/api/v3/orders/{order_id}")
    assert get_res.status_code == 200
    assert get_res.json()["petIds"][0]["quantity"] == 1
    assert get_res.json()["status"] == make_orders[0].status

    get_res = client.get(f"/api/v3/orders/0")
    assert get_res.status_code == 404
    assert "Order not found" in str(get_res.json()["detail"])


@pytest.mark.anyio
async def test_update_order(client, make_orders):
    order_id = make_orders[0].id
    shipDate = make_orders[0].shipDate + datetime.timedelta(days=7)
    shipDate = shipDate.strftime("%Y-%m-%d")
    data = {"status": "approved", "shipDate": shipDate}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert put_res.status_code == 200
    assert put_res.json()["status"] == data["status"]
    assert put_res.json()["shipDate"] == data["shipDate"]

    # Confirm
    get_res = client.get(f"/api/v3/orders/{order_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == data["status"]
    assert put_res.json()["shipDate"] == data["shipDate"]


@pytest.mark.anyio
async def test_update_order_pets(client, make_pets, make_orders):
    order_id = make_orders[0].id
    petIds = [{"petId": make_pets[2].id, "quantity": 5}]
    data = {"petIds": petIds}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert put_res.status_code == 200
    assert put_res.json()["petIds"][0]["petId"] == data["petIds"][0]["petId"]
    assert put_res.json()["petIds"][0]["quantity"] == data["petIds"][0]["quantity"]

    # Confirm
    get_res = client.get(f"/api/v3/orders/{order_id}")
    assert get_res.status_code == 200
    assert get_res.json()["petIds"][0]["petId"] == data["petIds"][0]["petId"]
    assert get_res.json()["petIds"][0]["quantity"] == data["petIds"][0]["quantity"]


@pytest.mark.anyio
async def test_update_order_validations(client, make_orders):
    order_id = make_orders[0].id
    data = {"shipDate": "77777-jj-8888"}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert put_res.status_code == 400
    assert "Invalid date format" in str(put_res.json()["detail"])

    petIds = [{"quantity": 4, "petId": 0}]
    data = {"petIds": petIds}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert put_res.status_code == 400
    assert "Invalid petId" in put_res.json()["detail"]


@pytest.mark.anyio
async def test_get_orders(client, make_orders):
    get_res = client.get(f"/api/v3/orders/")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 2

    params = {"limit": 1}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1

    params = {"limit": 101, "offset": 0}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 400
    assert "is greater than the maximum of" in get_res.json()["detail"]


@pytest.mark.anyio
async def test_get_orders_by_petid(client, make_pets, make_orders):
    params = {"petId": make_pets[0].id}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["petIds"][0]["petId"] == make_pets[0].id


@pytest.mark.anyio
async def test_get_orders_with_pets(client, make_pets, make_orders):
    params = {"includePets": "yes"}
    order_id = make_orders[0].id
    get_res = client.get(f"/api/v3/orders/{order_id}", params=params)
    assert get_res.status_code == 200
    assert "pets" in get_res.json()
    assert get_res.json()["pets"][0]["id"] == make_pets[0].id
    assert get_res.json()["pets"][0]["name"] == make_pets[0].name

    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 2
    assert "pets" in get_res.json()[0]
    assert get_res.json()[0]["pets"][0]["id"] == make_pets[0].id
    assert get_res.json()[0]["pets"][0]["name"] == make_pets[0].name


@pytest.mark.anyio
async def test_get_orders_by_status(client, make_orders):
    params = {"status": make_orders[0].status}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["status"] == make_orders[0].status

    params = {"status": "approvedxx"}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 400
    assert "'approvedxx' is not one of" in str(get_res.json()["detail"])


@pytest.mark.anyio
async def test_delete_order(client, make_orders):
    order_id = make_orders[0].id
    del_res = client.delete(f"/api/v3/orders/{order_id}")
    assert del_res.status_code == 204

    # Confirm
    check = client.get(f"/api/v3/orders/{order_id}")
    assert check.status_code == 404
