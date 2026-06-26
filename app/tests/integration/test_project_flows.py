import pytest
from httpx import AsyncClient
from app.models.category import Category

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
# Flujo: usuario crea proyecto → admin lo rechaza → no aparece en explore
# ---------------------------------------------------------------
@pytest.mark.asyncio
async def test_project_reject_flow(
    client: AsyncClient, standard_user_auth_headers: dict, admin_auth_headers: dict
):
    create_resp = await client.post(
        PROJECTS_URL, json=PROJECT_PAYLOAD, headers=standard_user_auth_headers
    )
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]

    reject_resp = await client.patch(
        f"{ADMIN_PROJECTS_URL}/{project_id}/reject",
        json={"reason": "Incomplete information provided."},
        headers=admin_auth_headers,
    )
    assert reject_resp.status_code == 200
    assert reject_resp.json()["state"] == "REJECTED"

    explore_resp = await client.get(
        f"{PROJECTS_URL}/explore", headers=standard_user_auth_headers
    )
    assert explore_resp.json()["total"] == 0


# ---------------------------------------------------------------
# Flujo: admin lista todos los proyectos
# ---------------------------------------------------------------
@pytest.mark.asyncio
async def test_admin_list_all_projects(
    client: AsyncClient, standard_user_auth_headers: dict, admin_auth_headers: dict
):
    for i in range(3):
        await client.post(
            PROJECTS_URL,
            json={**PROJECT_PAYLOAD, "name": f"Project {i}", "suffix": f"FTB{i}"},
            headers=standard_user_auth_headers,
        )

    response = await client.get(ADMIN_PROJECTS_URL, headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 3


# ---------------------------------------------------------------
# Flujo: solo admin puede aprobar/rechazar
# ---------------------------------------------------------------
@pytest.mark.asyncio
async def test_standard_user_cannot_approve(
    client: AsyncClient, standard_user_auth_headers: dict
):
    create_resp = await client.post(
        PROJECTS_URL, json=PROJECT_PAYLOAD, headers=standard_user_auth_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.patch(
        f"{ADMIN_PROJECTS_URL}/{project_id}/approve",
        headers=standard_user_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_standard_user_cannot_reject(
    client: AsyncClient, standard_user_auth_headers: dict
):
    create_resp = await client.post(
        PROJECTS_URL, json=PROJECT_PAYLOAD, headers=standard_user_auth_headers
    )
    project_id = create_resp.json()["id"]

    response = await client.patch(
        f"{ADMIN_PROJECTS_URL}/{project_id}/reject",
        json={"reason": "Not eligible."},
        headers=standard_user_auth_headers,
    )
    assert response.status_code == 403


# ---------------------------------------------------------------
# Flujo: aprobar proyecto inexistente
# ---------------------------------------------------------------
@pytest.mark.asyncio
async def test_approve_project_not_found(client: AsyncClient, admin_auth_headers: dict):
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await client.patch(
        f"{ADMIN_PROJECTS_URL}/{fake_id}/approve",
        headers=admin_auth_headers,
    )
    assert response.status_code == 404
