import pytest
from httpx import AsyncClient

ADMIN_URL = "/admin/categories"
USER_URL = "/categories"

CATEGORY_PAYLOAD = {
    "name": "Football",
    "description": "Football related category",
}


# ---------------------------------------------------------------
# POST /admin/categories
# ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_category_success(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post(ADMIN_URL, json=CATEGORY_PAYLOAD, headers=admin_auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Football"
    assert data["description"] == "Football related category"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_category_no_description(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post(ADMIN_URL, json={"name": "Basketball"}, headers=admin_auth_headers)

    assert response.status_code == 201
    assert response.json()["description"] is None


@pytest.mark.asyncio
async def test_create_category_unauthorized_standard_user(client: AsyncClient, standard_user_auth_headers: dict):
    response = await client.post(ADMIN_URL, json=CATEGORY_PAYLOAD, headers=standard_user_auth_headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_category_unauthorized(client: AsyncClient):
    response = await client.post(ADMIN_URL, json=CATEGORY_PAYLOAD)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_category_missing_name(client: AsyncClient, admin_auth_headers: dict):
    response = await client.post(ADMIN_URL, json={"description": "No name"}, headers=admin_auth_headers)

    assert response.status_code == 422


# ---------------------------------------------------------------
# PATCH /admin/categories/{category_id}
# ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_category_success(client: AsyncClient, admin_auth_headers: dict):
    create_resp = await client.post(ADMIN_URL, json=CATEGORY_PAYLOAD, headers=admin_auth_headers)
    category_id = create_resp.json()["id"]

    response = await client.patch(
        f"{ADMIN_URL}/{category_id}",
        json={"name": "Basketball", "description": "Basketball category"},
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Basketball"
    assert data["description"] == "Basketball category"


@pytest.mark.asyncio
async def test_update_category_not_found(client: AsyncClient, admin_auth_headers: dict):
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await client.patch(
        f"{ADMIN_URL}/{fake_id}",
        json={"name": "Tennis"},
        headers=admin_auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_category_unauthorized(client: AsyncClient, standard_user_auth_headers: dict):
    response = await client.patch(
        f"{ADMIN_URL}/00000000-0000-0000-0000-000000000000",
        json={"name": "Tennis"},
        headers=standard_user_auth_headers,
    )

    assert response.status_code == 403


# ---------------------------------------------------------------
# GET /admin/categories
# ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_list_categories_empty(client: AsyncClient, admin_auth_headers: dict):
    response = await client.get(ADMIN_URL, headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


@pytest.mark.asyncio
async def test_admin_list_categories_after_create(client: AsyncClient, admin_auth_headers: dict):
    await client.post(ADMIN_URL, json=CATEGORY_PAYLOAD, headers=admin_auth_headers)
    await client.post(ADMIN_URL, json={"name": "Basketball"}, headers=admin_auth_headers)

    response = await client.get(ADMIN_URL, headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["results"]) == 2


@pytest.mark.asyncio
async def test_admin_list_categories_search(client: AsyncClient, admin_auth_headers: dict):
    await client.post(ADMIN_URL, json={"name": "Football"}, headers=admin_auth_headers)
    await client.post(ADMIN_URL, json={"name": "Basketball"}, headers=admin_auth_headers)

    response = await client.get(f"{ADMIN_URL}?search=Foot", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["results"][0]["name"] == "Football"


@pytest.mark.asyncio
async def test_admin_list_categories_pagination(client: AsyncClient, admin_auth_headers: dict):
    for i in range(5):
        await client.post(ADMIN_URL, json={"name": f"Category {i}"}, headers=admin_auth_headers)

    response = await client.get(f"{ADMIN_URL}?page=1&page_size=3", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["results"]) == 3


# ---------------------------------------------------------------
# GET /admin/categories/{category_id}
# ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_get_category_success(client: AsyncClient, admin_auth_headers: dict):
    create_resp = await client.post(ADMIN_URL, json=CATEGORY_PAYLOAD, headers=admin_auth_headers)
    category_id = create_resp.json()["id"]

    response = await client.get(f"{ADMIN_URL}/{category_id}", headers=admin_auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == category_id
    assert response.json()["name"] == "Football"


@pytest.mark.asyncio
async def test_admin_get_category_not_found(client: AsyncClient, admin_auth_headers: dict):
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(f"{ADMIN_URL}/{fake_id}", headers=admin_auth_headers)

    assert response.status_code == 404


# ---------------------------------------------------------------
# GET /categories (standard user)
# ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_user_list_categories_empty(client: AsyncClient, standard_user_auth_headers: dict):
    response = await client.get(USER_URL, headers=standard_user_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


@pytest.mark.asyncio
async def test_user_list_categories(client: AsyncClient, admin_auth_headers: dict, standard_user_auth_headers: dict):
    await client.post(ADMIN_URL, json={"name": "Football"}, headers=admin_auth_headers)
    await client.post(ADMIN_URL, json={"name": "Basketball"}, headers=admin_auth_headers)

    response = await client.get(USER_URL, headers=standard_user_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_user_list_categories_unauthorized(client: AsyncClient):
    response = await client.get(USER_URL)

    assert response.status_code == 401


# ---------------------------------------------------------------
# GET /categories/{category_id} (standard user)
# ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_user_get_category_success(client: AsyncClient, admin_auth_headers: dict, standard_user_auth_headers: dict):
    create_resp = await client.post(ADMIN_URL, json=CATEGORY_PAYLOAD, headers=admin_auth_headers)
    category_id = create_resp.json()["id"]

    response = await client.get(f"{USER_URL}/{category_id}", headers=standard_user_auth_headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Football"


@pytest.mark.asyncio
async def test_user_get_category_not_found(client: AsyncClient, standard_user_auth_headers: dict):
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(f"{USER_URL}/{fake_id}", headers=standard_user_auth_headers)

    assert response.status_code == 404
