import pytest


@pytest.mark.asyncio
async def test_create_user(async_client):
    response = await async_client.post("/users", json={})
    assert 201 == response.status_code
    data = response.json()
    assert data["policy_number"] == 1
    assert {"policy_number": 1} == response.json()


@pytest.mark.asyncio
async def test_get_users(async_client):
    await async_client.post("/users", json={})
    await async_client.post("/users", json={})
    await async_client.post("/users", json={})
    response = await async_client.get("/users")
    assert 200 == response.status_code
    response.json()
    assert {"users": [{"policy_number": 1}, {"policy_number": 2}, {"policy_number": 3}]} == response.json()
