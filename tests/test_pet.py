import pytest


@pytest.mark.anyio
async def test_add_pet(client):
    pet = {"name": "doggie", "status": "available"}

    response = client.post("/api/v3/pets", json=pet)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "doggie"
    assert data["status"] == "available"


@pytest.mark.anyio
async def test_get_pet_by_id(client):
    # First, add a pet
    new_pet = {"name": "whiskers"}
    post_res = client.post("/api/v3/pets", json=new_pet)
    assert post_res.status_code == 201
    pet_id = post_res.json()["id"]

    get_res = client.get(f"/api/v3/pets/{pet_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "whiskers"
    assert get_res.json()["status"] == "available"

    get_res = client.get(f"/api/v3/pets/0")
    assert get_res.status_code == 404


@pytest.mark.anyio
async def test_update_pet(client):
    # First, add a pet
    new_pet = {"name": "whiskers", "status": "pending"}
    post_res = client.post("/api/v3/pets", json=new_pet)
    pet_id = post_res.json()["id"]

    data = {"name": "whiskers_changed"}
    get_res = client.put(f"/api/v3/pets/{pet_id}", json=data)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "whiskers_changed"

    get_res = client.get(f"/api/v3/pets/{pet_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "whiskers_changed"

    data = {"status": "sold"}
    put_res = client.put(f"/api/v3/pets/{pet_id}", json=data)
    assert put_res.status_code == 200
    assert put_res.json()["status"] == "sold"

    get_res = client.get(f"/api/v3/pets/{pet_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "sold"


@pytest.mark.anyio
async def test_get_pets(client):
    # First, add a pet
    new_pet = {"name": "whiskers", "status": "pending"}
    post_res = client.post("/api/v3/pets", json=new_pet)
    assert post_res.status_code == 201

    # Add a second pet
    new_pet = {"name": "whiskers2", "status": "pending"}
    post_res = client.post("/api/v3/pets", json=new_pet)
    assert post_res.status_code == 201

    get_res = client.get(f"/api/v3/pets/")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 2
    assert get_res.json()[0]["name"] == "whiskers"


@pytest.mark.anyio
async def test_get_pets_by_status(client):
    # First, add a pet
    new_pet = {"name": "whiskers", "status": "pending"}
    post_res = client.post("/api/v3/pets", json=new_pet)
    assert post_res.status_code == 201

    # Add a second pet
    new_pet = {"name": "whiskers2", "status": "sold"}
    post_res = client.post("/api/v3/pets", json=new_pet)
    assert post_res.status_code == 201

    params = {"status": "pending"}
    get_res = client.get(f"/api/v3/pets/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["name"] == "whiskers"

    params = {"status": "pendingxx"}
    get_res = client.get(f"/api/v3/pets/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 0


@pytest.mark.anyio
async def test_get_pets_by_name(client):
    # First, add a pet
    new_pet = {"name": "whiskers1233H", "status": "pending"}
    post_res = client.post("/api/v3/pets", json=new_pet)
    assert post_res.status_code == 201
    # Add a second pet
    new_pet = {"name": "whiskers2", "status": "pending"}
    post_res = client.post("/api/v3/pets", json=new_pet)
    assert post_res.status_code == 201

    params = {"name": "whiskers1233H"}
    get_res = client.get(f"/api/v3/pets/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["name"] == "whiskers1233H"

    params = {"status": "whiskers1233Hxx"}
    get_res = client.get(f"/api/v3/pets/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 0


@pytest.mark.anyio
async def test_delete_pet(client):
    new_pet = {
        "name": "delete_me",
    }
    res = client.post("/api/v3/pets", json=new_pet)
    pet_id = res.json()["id"]

    del_res = client.delete(f"/api/v3/pets/{pet_id}")
    assert del_res.status_code == 204

    # verify deleted
    check = client.get(f"/api/v3/pets/{pet_id}")
    assert check.status_code == 404
