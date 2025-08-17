import pytest


@pytest.mark.anyio
async def test_add_order(client, make_pets):
    order = {"quantity": 4}

    post_res = client.post("/api/v3/orders", json=order)
    assert post_res.status_code == 400
    data = post_res.json()
    assert "required property" in data["detail"]

    order["petId"] = 0
    post_res = client.post("/api/v3/orders", json=order)
    assert post_res.status_code == 400
    assert "Invalid petId" in post_res.json()["detail"]

    # Add a pet id
    get_res = client.get(f"/api/v3/pets/")
    assert get_res.status_code == 200
    assert len(get_res.json()) > 1

    pet = get_res.json()[0]
    order["petId"] = pet["id"]
    post_res = client.post("/api/v3/orders", json=order)
    assert post_res.status_code == 201
    data = post_res.json()
    assert data["quantity"] == 4
    assert data["petId"] == pet["id"]
    assert data["status"] == "placed"


@pytest.mark.anyio
async def test_get_order_by_id(client, make_pets):
    # First, add a order
    get_res = client.get(f"/api/v3/pets/")
    pet = get_res.json()[0]
    new_order = {"petId": pet["id"], "quantity": 4}
    post_res = client.post("/api/v3/orders", json=new_order)
    assert post_res.status_code == 201
    order_id = post_res.json()["id"]

    get_res = client.get(f"/api/v3/orders/{order_id}")
    assert get_res.status_code == 200
    assert get_res.json()["quantity"] == 4
    assert get_res.json()["status"] == "placed"

    get_res = client.get(f"/api/v3/orders/0")
    assert get_res.status_code == 404
    assert "Order not found" in str(get_res.json()["detail"])


@pytest.mark.anyio
async def test_update_order(client, make_pets):
    # First, add a order
    get_res = client.get(f"/api/v3/pets/")
    pet = get_res.json()[0]
    new_order = {"petId": pet["id"], "quantity": 4}
    post_res = client.post("/api/v3/orders", json=new_order)
    order = post_res.json()
    order_id = order["id"]

    data = {"shipDate": "77777-jj-8888"}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert put_res.status_code == 400
    assert "Invalid date format" in str(put_res.json()["detail"])

    data = {"status": "approved", "quantity": 2, "shipDate": order["shipDate"]}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert put_res.status_code == 200
    assert put_res.json()["status"] == data["status"]
    assert put_res.json()["quantity"] == data["quantity"]

    get_res = client.get(f"/api/v3/orders/{order_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == data["status"]
    assert get_res.json()["quantity"] == data["quantity"]

    data = {"petId": 0}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert put_res.status_code == 400
    assert "Invalid petId" in put_res.json()["detail"]


@pytest.mark.anyio
async def test_get_orders(client, make_pets):
    # First, add a order
    get_res = client.get(f"/api/v3/pets/")
    pet = get_res.json()[0]
    pet2 = get_res.json()[1]
    new_order = {"petId": pet["id"], "quantity": 4}
    post_res = client.post("/api/v3/orders", json=new_order)
    assert post_res.status_code == 201

    # Add a second order
    new_order = {"petId": pet2["id"], "quantity": 1}
    post_res = client.post("/api/v3/orders", json=new_order)
    assert post_res.status_code == 201

    get_res = client.get(f"/api/v3/orders/")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 2


@pytest.mark.anyio
async def test_get_orders_by_petid(client, make_pets):
    # First, add a order
    get_res = client.get(f"/api/v3/pets/")
    pet = get_res.json()[0]
    pet2 = get_res.json()[1]
    new_order = {"petId": pet["id"], "quantity": 4}
    post_res = client.post("/api/v3/orders", json=new_order)
    assert post_res.status_code == 201

    # Add a second order
    new_order = {"petId": pet2["id"], "quantity": 1}
    post_res = client.post("/api/v3/orders", json=new_order)
    assert post_res.status_code == 201

    params = {"petId": pet["id"]}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["quantity"] == 4

    params = {"status": "pendingxx"}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 0


@pytest.mark.anyio
async def test_get_orders_by_status(client, make_pets):
    # First, add a order
    get_res = client.get(f"/api/v3/pets/")
    pet = get_res.json()[0]
    pet2 = get_res.json()[1]
    new_order = {"petId": pet["id"], "quantity": 4}
    post_res = client.post("/api/v3/orders", json=new_order)
    assert post_res.status_code == 201

    # Add a second order
    new_order = {"petId": pet2["id"], "status": "approved", "quantity": 1}
    post_res = client.post("/api/v3/orders", json=new_order)
    assert post_res.status_code == 201

    params = {"status": "placed"}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["quantity"] == 4

    params = {"status": "approvedxx"}
    get_res = client.get(f"/api/v3/orders/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 0


@pytest.mark.anyio
async def test_delete_order(client, make_pets):
    # First, add a order
    get_res = client.get(f"/api/v3/pets/")
    pet = get_res.json()[0]
    new_order = {"petId": pet["id"], "quantity": 4}
    post_res = client.post("/api/v3/orders", json=new_order)
    assert post_res.status_code == 201
    order_id = post_res.json()["id"]

    del_res = client.delete(f"/api/v3/orders/{order_id}")
    assert del_res.status_code == 204

    # verify deleted
    check = client.get(f"/api/v3/orders/{order_id}")
    assert check.status_code == 404
