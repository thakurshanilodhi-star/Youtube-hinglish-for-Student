"""Authentication tests."""
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/register", params={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        })
    assert response.status_code == 200
    assert "user_id" in response.json()

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Register first
        await ac.post("/api/v1/auth/register", params={
            "email": "login@example.com",
            "password": "testpass123"
        })
        # Login
        response = await ac.post("/api/v1/auth/login", data={
            "username": "login@example.com",
            "password": "testpass123"
        })
    assert response.status_code == 200
    assert "access_token" in response.json()
