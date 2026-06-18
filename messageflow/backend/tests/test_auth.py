# pytest tests for auth and token flows
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_login_refresh_logout():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # register
        res = await client.post('/auth/register', json={"company_name":"TestCo","name":"Admin","email":"test+1@example.com","password":"password"})
        assert res.status_code == 200
        data = res.json()
        assert 'company_id' in data
        # login
        res = await client.post('/auth/login', json={"email":"test+1@example.com","password":"password"})
        assert res.status_code == 200
        tokens = res.json()
        assert 'access_token' in tokens and 'refresh_token' in tokens
        # refresh
        res = await client.post('/auth/refresh', json={"refresh_token": tokens['refresh_token']})
        assert res.status_code == 200
        new = res.json()
        assert 'access_token' in new and 'refresh_token' in new
        # logout old refresh
        res = await client.post('/auth/logout', json={"refresh_token": tokens['refresh_token']})
        assert res.status_code == 200
