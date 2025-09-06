# test_pet.py
from unittest.mock import MagicMock

import pytest
import logging


@pytest.mark.anyio
async def test_add_pet_logging(client, caplog):
    caplog.set_level(logging.DEBUG, logger="app.pet")
    data = {"name": "doggie", "status": "available"}
    post_res = client.post("/api/v3/pets", json=data)
    assert post_res.status_code == 201
    assert "Adding pet with data" in caplog.text


@pytest.mark.anyio
async def test_get_pet_logging(client, make_pets, caplog):
    caplog.set_level(logging.DEBUG, logger="app.pet")
    get_res = client.get(f"/api/v3/pets/{make_pets[0].id}")
    assert get_res.status_code == 200
    assert "Fetching pet with id" in caplog.text

    get_res = client.get(f"/api/v3/pets/0")
    assert get_res.status_code == 404
    assert "Pet not found" in caplog.text


@pytest.mark.anyio
async def test_logged_database_exception(
    client, make_pets, make_orders, bad_session, caplog
):
    caplog.set_level(logging.ERROR, logger="app.pet")
    data = {"name": "doggie", "status": "available"}
    post_res = client.post("/api/v3/pets", json=data)
    assert post_res.status_code == 500
    #  Confirm trace is in log file, but not response
    assert "views/pet.py" not in post_res.text
    assert "views/pet.py" in caplog.text

    pet_id = make_pets[0].id
    data = {"name": "whiskers_changed", "status": "sold"}
    put_res = client.put(f"/api/v3/pets/{pet_id}", json=data)
    assert put_res.status_code == 500
    #  Confirm trace is in log file, but not response
    assert "views/pet.py" not in put_res.text
    assert "views/pet.py" in caplog.text

    order_id = make_orders[0].id
    data = {"status": "approved", "quantity": 2}
    put_res = client.put(f"/api/v3/orders/{order_id}", json=data)
    assert "views/order.py" not in put_res.text
    assert "views/order.py" in caplog.text
