import pytest
from httpx import AsyncClient

STANDARD_URL = "/users"
ADMIN_URL = "/admin/users"


# ---------------------------------------------------------------
# POST /users/register
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post(
        f"{STANDARD_URL}/register",
        json={
            "username": "newuser",
            "name": "New",
            "last_name": "User",
            "email": "new@depfund.com",
            "password": "Password123!",
            "birthdate": "2000-01-01",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@depfund.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "username": "user1",
        "name": "User",
        "last_name": "One",
        "email": "dup@depfund.com",
        "password": "Password123!",
        "birthdate": "2000-01-01",
    }
    await client.post(f"{STANDARD_URL}/register", json=payload)

    response = await client.post(
        f"{STANDARD_URL}/register",
        json={
            **payload,
            "username": "user2",  # distinto username, mismo email
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    payload = {
        "username": "sameuser",
        "name": "User",
        "last_name": "One",
        "email": "user1@depfund.com",
        "password": "Password123!",
        "birthdate": "2000-01-01",
    }
    await client.post(f"{STANDARD_URL}/register", json=payload)

    response = await client.post(
        f"{STANDARD_URL}/register",
        json={
            **payload,
            "email": "user2@depfund.com",  # distinto email, mismo username
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    response = await client.post(
        f"{STANDARD_URL}/register",
        json={
            "username": "shortpass",
            "name": "User",
            "last_name": "One",
            "email": "short@depfund.com",
            "password": "123",
            "birthdate": "2000-01-01",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient):
    response = await client.post(
        f"{STANDARD_URL}/register",
        json={
            "username": "incomplete",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_minor_age(client: AsyncClient):
    response = await client.post(
        f"{STANDARD_URL}/register",
        json={
            "username": "minoruser",
            "name": "Minor",
            "last_name": "User",
            "email": "minor@depfund.com",
            "password": "Password123!",
            "birthdate": "2015-01-01",
        },
    )
    assert response.status_code == 400


# ---------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient, standard_user_auth_headers: dict):
    response = await client.get(
        f"{STANDARD_URL}/me", headers=standard_user_auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@depfund.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get(f"{STANDARD_URL}/me")

    assert response.status_code == 401


# ---------------------------------------------------------------
# PATCH /users/me
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_me_success(client: AsyncClient, standard_user_auth_headers: dict):
    response = await client.patch(
        f"{STANDARD_URL}/me",
        json={
            "name": "Updated",
            "last_name": "Name",
        },
        headers=standard_user_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["last_name"] == "Name"


@pytest.mark.asyncio
async def test_update_me_unauthorized(client: AsyncClient):
    response = await client.patch(f"{STANDARD_URL}/me", json={"name": "Hacked"})

    assert response.status_code == 401


# ---------------------------------------------------------------
# POST /users/me/change-password
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_change_password_success(
    client: AsyncClient, standard_user_auth_headers: dict
):
    response = await client.post(
        f"{STANDARD_URL}/me/change-password",
        json={
            "old_password": "UserPassword123!",
            "new_password": "NewPassword123!",
        },
        headers=standard_user_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_change_password_wrong_old(
    client: AsyncClient, standard_user_auth_headers: dict
):
    response = await client.post(
        f"{STANDARD_URL}/me/change-password",
        json={
            "old_password": "WrongPassword!",
            "new_password": "NewPassword123!",
        },
        headers=standard_user_auth_headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_change_password_too_short(
    client: AsyncClient, standard_user_auth_headers: dict
):
    response = await client.post(
        f"{STANDARD_URL}/me/change-password",
        json={
            "old_password": "UserPassword123!",
            "new_password": "123",
        },
        headers=standard_user_auth_headers,
    )

    assert response.status_code == 422


# ---------------------------------------------------------------
# DELETE /users/me
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_me_success(client: AsyncClient, standard_user_auth_headers: dict):
    response = await client.delete(
        f"{STANDARD_URL}/me", headers=standard_user_auth_headers
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_me_unauthorized(client: AsyncClient):
    response = await client.delete(f"{STANDARD_URL}/me")

    assert response.status_code == 401


# ---------------------------------------------------------------
# POST /admin/users
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_admin_user_success(client: AsyncClient):
    import os

    response = await client.post(
        ADMIN_URL,
        json={
            "admin_secret_key": os.getenv("ADMIN_SECRET_KEY", "develop"),
            "username": "newadmin",
            "name": "Admin",
            "last_name": "User",
            "email": "newadmin@depfund.com",
            "password": "AdminPass123!",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newadmin"
    assert data["email"] == "newadmin@depfund.com"


@pytest.mark.asyncio
async def test_create_admin_user_wrong_secret(client: AsyncClient):
    response = await client.post(
        ADMIN_URL,
        json={
            "admin_secret_key": "wrong-secret",
            "username": "hacker",
            "name": "Hack",
            "last_name": "Er",
            "email": "hacker@depfund.com",
            "password": "AdminPass123!",
        },
    )

    assert response.status_code in (401, 403)


# ---------------------------------------------------------------
# GET /admin/users/me
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_get_me_success(client: AsyncClient, admin_auth_headers: dict):
    response = await client.get(f"{ADMIN_URL}/me", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@depfund.com"
    assert data["username"] == "admintest"


@pytest.mark.asyncio
async def test_admin_get_me_unauthorized(client: AsyncClient):
    response = await client.get(f"{ADMIN_URL}/me")

    assert response.status_code == 401


# ---------------------------------------------------------------
# PATCH /admin/users/me
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_update_me_success(client: AsyncClient, admin_auth_headers: dict):
    response = await client.patch(
        f"{ADMIN_URL}/me",
        json={
            "name": "UpdatedAdmin",
        },
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedAdmin"


# ---------------------------------------------------------------
# POST /admin/users/me/change-password
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_change_password_success(
    client: AsyncClient, admin_auth_headers: dict
):
    response = await client.post(
        f"{ADMIN_URL}/me/change-password",
        json={
            "old_password": "AdminPassword123!",
            "new_password": "NewAdminPass123!",
        },
        headers=admin_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_admin_change_password_wrong_old(
    client: AsyncClient, admin_auth_headers: dict
):
    response = await client.post(
        f"{ADMIN_URL}/me/change-password",
        json={
            "old_password": "WrongPassword!",
            "new_password": "NewAdminPass123!",
        },
        headers=admin_auth_headers,
    )

    assert response.status_code == 400


# ---------------------------------------------------------------
# GET /admin/users/users
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_list_users_empty(client: AsyncClient, admin_auth_headers: dict):
    response = await client.get(f"{ADMIN_URL}/users", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


@pytest.mark.asyncio
async def test_admin_list_users_after_register(
    client: AsyncClient, admin_auth_headers: dict, standard_user_auth_headers: dict
):
    response = await client.get(f"{ADMIN_URL}/users", headers=admin_auth_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1


# ---------------------------------------------------------------
# PATCH /admin/users/users/{user_id}/block
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_block_user(
    client: AsyncClient, admin_auth_headers: dict, standard_user_auth_headers: dict
):
    # Obtenemos el user id
    me_resp = await client.get(f"{STANDARD_URL}/me", headers=standard_user_auth_headers)
    user_id = me_resp.json()["id"]

    response = await client.patch(
        f"{ADMIN_URL}/users/{user_id}/block",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["blocked"] is True


@pytest.mark.asyncio
async def test_admin_block_user_not_found(
    client: AsyncClient, admin_auth_headers: dict
):
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await client.patch(
        f"{ADMIN_URL}/users/{fake_id}/block",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404


# ---------------------------------------------------------------
# DELETE /admin/users/me
# ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_delete_me_success(client: AsyncClient, admin_auth_headers: dict):
    response = await client.delete(f"{ADMIN_URL}/me", headers=admin_auth_headers)

    assert response.status_code == 204
