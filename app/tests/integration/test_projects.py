import pytest
from httpx import AsyncClient
from app.models.category import Category

BASE_URL = "/projects"
PROJECTS_URL = "/projects"
ADMIN_PROJECTS_URL = "/admin/projects"

PROJECT_PAYLOAD = {
    "name": "Football Academy",
    "description": "Funding for youth football academy",
    "total_amount": "50000.00",
    "min_amount": "10000.00",
    "suffix": "FTBL",
    "ubication": "Buenos Aires, Argentina",
    "category_ids": [],
    "estimated_development_days": 180,
}


# ---------------------------------------------------------------
# Flujo: usuario crea proyecto → admin lo aprueba → aparece en explore
# ---------------------------------------------------------------
@pytest.mark.skip(reason="Requiere entorno blockchain")
@pytest.mark.asyncio
async def test_project_approve_flow(
    client, standard_user_auth_headers, admin_auth_headers, db_session
):
    category = Category(name="Fútbol", description="Categoría de fútbol")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    payload = {**PROJECT_PAYLOAD, "category_ids": [str(category.id)]}
    create_resp = await client.post(
        PROJECTS_URL, json=payload, headers=standard_user_auth_headers
    )
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]

    explore_resp = await client.get(
        f"{PROJECTS_URL}/explore", headers=standard_user_auth_headers
    )
    assert explore_resp.json()["total"] == 0

    approve_resp = await client.patch(
        f"{ADMIN_PROJECTS_URL}/{project_id}/approve",
        headers=admin_auth_headers,
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["state"] == "APPROVED"

    explore_resp = await client.get(
        f"{PROJECTS_URL}/explore", headers=standard_user_auth_headers
    )
    assert explore_resp.json()["total"] == 1
    assert explore_resp.json()["results"][0]["id"] == project_id


# ---------------------------------------------------------------
# POST /projects
# ---------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_project_success(
    client: AsyncClient, standard_user_auth_headers: dict
):
    response = await client.post(
        BASE_URL, json=PROJECT_PAYLOAD, headers=standard_user_auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Football Academy"
    assert data["description"] == "Funding for youth football academy"
    assert data["total_amount"] == "50000.00"
    assert data["ubication"] == "Buenos Aires, Argentina"
    assert data["state"] is not None
    assert "id" in data
    assert "user_id" in data


@pytest.mark.asyncio
async def test_create_project_unauthorized(client: AsyncClient):
    response = await client.post(BASE_URL, json=PROJECT_PAYLOAD)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_project_missing_fields(
    client: AsyncClient, standard_user_auth_headers: dict
):
    response = await client.post(
        BASE_URL,
        json={"name": "Incomplete Project"},
        headers=standard_user_auth_headers,
    )
    assert response.status_code == 422


# ---------------------------------------------------------------
# GET /projects (mis proyectos)
# ---------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_my_projects_empty(
    client: AsyncClient, standard_user_auth_headers: dict
):
    response = await client.get(BASE_URL, headers=standard_user_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


@pytest.mark.asyncio
async def test_list_my_projects_after_create(
    client: AsyncClient, standard_user_auth_headers: dict
):
    await client.post(
        BASE_URL, json=PROJECT_PAYLOAD, headers=standard_user_auth_headers
    )

    response = await client.get(BASE_URL, headers=standard_user_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["results"][0]["name"] == "Football Academy"


@pytest.mark.asyncio
async def test_list_my_projects_pagination(
    client: AsyncClient, standard_user_auth_headers: dict
):
    for i in range(3):
        await client.post(
            BASE_URL,
            json={**PROJECT_PAYLOAD, "name": f"Project {i}", "suffix": f"FTB{i}"},
            headers=standard_user_auth_headers,
        )

    response = await client.get(
        f"{BASE_URL}?page=1&page_size=2", headers=standard_user_auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["results"]) == 2


# ---------------------------------------------------------------
# PATCH /projects/{project_id}
# ---------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_project_success(
    client: AsyncClient, standard_user_auth_headers: dict
):
    create_resp = await client.post(
        BASE_URL, json=PROJECT_PAYLOAD, headers=standard_user_auth_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.patch(
        f"{BASE_URL}/{project_id}",
        json={"description": "Updated description", "ubication": "Córdoba, Argentina"},
        headers=standard_user_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["ubication"] == "Córdoba, Argentina"


@pytest.mark.asyncio
async def test_update_project_unauthorized(
    client: AsyncClient, standard_user_auth_headers: dict
):
    create_resp = await client.post(
        BASE_URL, json=PROJECT_PAYLOAD, headers=standard_user_auth_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.patch(
        f"{BASE_URL}/{project_id}", json={"description": "Hacked"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_project_not_found(
    client: AsyncClient, standard_user_auth_headers: dict
):
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await client.patch(
        f"{BASE_URL}/{fake_id}",
        json={"description": "No existe"},
        headers=standard_user_auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------
# GET /projects/{project_id}
# ---------------------------------------------------------------
@pytest.mark.asyncio
@pytest.mark.skip("entorno")
async def test_get_project_success(
    client: AsyncClient, standard_user_auth_headers: dict
):
    create_resp = await client.post(
        BASE_URL, json=PROJECT_PAYLOAD, headers=standard_user_auth_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.get(
        f"{BASE_URL}/{project_id}", headers=standard_user_auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Football Academy"


@pytest.mark.asyncio
async def test_get_project_not_found(
    client: AsyncClient, standard_user_auth_headers: dict
):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"{BASE_URL}/{fake_id}", headers=standard_user_auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_project_unauthorized(
    client: AsyncClient, standard_user_auth_headers: dict
):
    create_resp = await client.post(
        BASE_URL, json=PROJECT_PAYLOAD, headers=standard_user_auth_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.get(f"{BASE_URL}/{project_id}")
    assert response.status_code == 401


# ---------------------------------------------------------------
# GET /projects/explore
# ---------------------------------------------------------------
@pytest.mark.asyncio
async def test_explore_projects_empty(
    client: AsyncClient, standard_user_auth_headers: dict
):
    response = await client.get(
        f"{BASE_URL}/explore", headers=standard_user_auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "results" in data


@pytest.mark.asyncio
async def test_explore_projects_pagination(
    client: AsyncClient, standard_user_auth_headers: dict
):
    for i in range(3):
        await client.post(
            BASE_URL,
            json={
                **PROJECT_PAYLOAD,
                "name": f"Explore Project {i}",
                "suffix": f"EXP{i}",
            },
            headers=standard_user_auth_headers,
        )

    response = await client.get(
        f"{BASE_URL}/explore?page=1&page_size=2", headers=standard_user_auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 2
