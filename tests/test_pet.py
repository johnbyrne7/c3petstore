import pytest


@pytest.mark.anyio
async def test_add_pet(client):
    data = {"name": "doggie", "description": "Noisey", "status": "available"}
    post_res = client.post("/api/v3/pets", json=data)
    assert post_res.status_code == 201
    assert post_res.json()["name"] == "doggie"
    assert post_res.json()["status"] == "available"


@pytest.mark.anyio
async def test_add_pet_validations(client):
    data = {"status": "available"}
    post_res = client.post("/api/v3/pets", json=data)
    assert post_res.status_code == 400
    assert "name' is a required property" in post_res.json()["detail"]


@pytest.mark.anyio
async def test_get_pet_by_id(client, make_pets):
    get_res = client.get(f"/api/v3/pets/{make_pets[0].id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == make_pets[0].name
    assert get_res.json()["description"] == make_pets[0].description
    assert get_res.json()["status"] == make_pets[0].status


@pytest.mark.anyio
async def test_get_pet_bad_id(client, make_pets):
    get_res = client.get(f"/api/v3/pets/0")
    assert get_res.status_code == 404


@pytest.mark.anyio
async def test_update_pet(client, make_pets):
    pet_id = make_pets[0].id
    data = {"name": "whiskers_changed", "status": "sold"}
    put_res = client.put(f"/api/v3/pets/{pet_id}", json=data)
    assert put_res.status_code == 200
    assert put_res.json()["name"] == "whiskers_changed"
    assert put_res.json()["status"] == "sold"

    # confirm
    get_res = client.get(f"/api/v3/pets/{pet_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "whiskers_changed"
    assert get_res.json()["status"] == "sold"


@pytest.mark.anyio
async def test_get_pets(client, make_pets):
    get_res = client.get(f"/api/v3/pets/")
    assert get_res.status_code == 200
    assert len(get_res.json()) == len(make_pets)
    assert get_res.json()[0]["name"] == make_pets[0].name

    params = {"limit": 1}
    get_res = client.get(f"/api/v3/pets/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1

    params = {"limit": 101, "offset": 0}
    get_res = client.get(f"/api/v3/pets/", params=params)
    assert get_res.status_code == 400
    assert "is greater than the maximum of" in get_res.json()["detail"]


@pytest.mark.anyio
async def test_get_pets_by_status(client, make_pets):
    params = {"status": make_pets[0].status}
    get_res = client.get(f"/api/v3/pets/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["status"] == make_pets[0].status
    assert get_res.json()[0]["name"] == make_pets[0].name

    params = {"status": "pendingxx"}
    get_res = client.get(f"/api/v3/pets/", params=params)
    assert get_res.status_code == 400
    assert "'pendingxx' is not one of" in str(get_res.json()["detail"])


@pytest.mark.anyio
async def test_get_pets_by_name(client, make_pets):
    params = {"name": make_pets[0].name}
    get_res = client.get(f"/api/v3/pets/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1
    assert get_res.json()[0]["name"] == make_pets[0].name

    params = {"name": "whiskers1233Hxx"}
    get_res = client.get(f"/api/v3/pets/", params=params)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 0


@pytest.mark.anyio
async def test_delete_pet(client, make_pets):
    pet_id = make_pets[0].id
    del_res = client.delete(f"/api/v3/pets/{pet_id}")
    assert del_res.status_code == 204

    # verify deleted
    check = client.get(f"/api/v3/pets/{pet_id}")
    assert check.status_code == 404
