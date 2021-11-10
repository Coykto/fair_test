import pytest

from main import init_app
from fair.repository import (
    CarRepository,
    TestRepository,
)


@pytest.fixture()
def car():
    return {"model": "test_model", "year": 2021}


@pytest.mark.parametrize("repository", [CarRepository, TestRepository])
async def test_post_must_return_201_status_and_location_of_a_new_object_in_header(
    aiohttp_client, car, repository
):
    client = await aiohttp_client(await init_app(repository))
    resp = await client.post("/", json=car)
    assert resp.status == 201
    assert "Location" in resp.headers


@pytest.mark.parametrize("repository", [CarRepository, TestRepository])
async def test_get_by_id_returns_data(aiohttp_client, car, repository):
    client = await aiohttp_client(await init_app(repository))
    repository = repository()
    car_id = await repository.create(car)

    resp = await client.get(f"/{car_id}")
    assert resp.status == 200
    content = await resp.json()
    assert len(content) > 0
    for key, value in content.items():
        if key == "id":
            assert value == car_id
            continue
        assert value == car[key]


@pytest.mark.parametrize("repository", [CarRepository, TestRepository])
async def test_update_car_updates_data(aiohttp_client, car, repository):
    client = await aiohttp_client(await init_app(repository))
    repository = repository()
    car_id = await repository.create(car)

    update_data = {"id": car_id, "model": "another_model", "year": 3000}

    resp = await client.put(f"/", json=update_data)
    assert resp.status == 200

    result_car = await repository.get(car_id)
    assert update_data == result_car


@pytest.mark.parametrize("repository", [CarRepository, TestRepository])
async def test_patch_car_partially_updates_data(aiohttp_client, car, repository):
    client = await aiohttp_client(await init_app(repository))
    repository = repository()
    car_id = await repository.create(car)

    patch_data = {"id": car_id, "year": 3000}

    resp = await client.patch(f"/{car_id}", json=patch_data)
    assert resp.status == 200

    result_car = await repository.get(car_id)
    assert result_car["id"] == car_id
    assert result_car["model"] == car["model"]
    assert result_car["year"] == patch_data["year"]
    assert result_car["year"] != car["year"]


@pytest.mark.parametrize("repository", [CarRepository, TestRepository])
async def test_delete_car_deletes_car(aiohttp_client, car, repository):
    client = await aiohttp_client(await init_app(repository))
    repository = repository()
    car_id = await repository.create(car)

    resp = await client.delete(f"/{car_id}")
    assert resp.status == 204

    result_car = await repository.get(car_id)
    assert result_car is None


@pytest.mark.parametrize("repository", [CarRepository, TestRepository])
async def test_list_returns_list_of_all_cars(aiohttp_client, car, repository):
    client = await aiohttp_client(await init_app(repository))
    repository = repository()
    car_id = await repository.create(car)
    car["id"] = car_id

    another_car = {"model": "another model", "year": 5000}
    another_car_id = await repository.create(another_car)
    another_car["id"] = another_car_id

    resp = await client.get(f"/")
    assert resp.status == 200

    content = await resp.json()
    assert len(content) == 2
    for item in content:
        if item["id"] == car_id:
            assert item == car
        else:
            assert item == another_car
