import pytest


@pytest.mark.asyncio
async def test_create_user(async_client):
    response = await async_client.post("/users", json={})
    assert 201 == response.status_code
    data = response.json()
    assert data["id"] == 1
    assert {"id": 1} == response.json()
