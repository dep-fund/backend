import pytest
from httpx import AsyncClient

PROJECTS_URL = "/projects"
ADMIN_PROJECTS_URL = "/admin/projects"


PROJECT_PAYLOAD = {
    "name": "Football Academy",
    "description": "Funding for youth football academy",
    "total_amount": "50000.00",
    "min_amount": "1000.00",
    "annual_expenses": "10000.00",
    "annual_gross_profit": "25000.00",
    "suffix": "ARS",
    "ubication": "Buenos Aires, Argentina",
    "category_ids": [],
    "estimated_development_days": 180,
}

# ---------------------------------------------------------------
# Flujo: usuario crea proyecto → admin lo aprueba → aparece en explore
# ---------------------------------------------------------------

"""
@pytest.mark.asyncio
async def test_project_approve_flow(client: AsyncClient, standard_user_auth_headers: dict, admin_auth_headers: dict):
    create_resp = await client.post(PROJECTS_URL, json=PROJECT_PAYLOAD, headers=standard_user_auth_headers)
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]

    explore_resp = await client.get(f"{PROJECTS_URL}/explore", headers=standard_user_auth_headers)
    assert explore_resp.json()["total"] == 0

    approve_resp = await client.patch(
        f"{ADMIN_PROJECTS_URL}/{project_id}/approve",
        headers=admin_auth_headers,
    )
    print("APPROVE BODY:", approve_resp.json())
    assert approve_resp.status_code == 200
    assert approve_resp.json()["state"] == "APPROVED"

    explore_resp = await client.get(f"{PROJECTS_URL}/explore", headers=standard_user_auth_headers)
    assert explore_resp.json()["total"] == 1
    assert explore_resp.json()["results"][0]["id"] == project_id

    
    """
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
            json={**PROJECT_PAYLOAD, "name": f"Project {i}"},
            headers=standard_user_auth_headers,
        )

    response = await client.get(ADMIN_PROJECTS_URL, headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 3


# ---------------------------------------------------------------
# Flujo: explore muestra solo aprobados
# ---------------------------------------------------------------
"""
@pytest.mark.asyncio
async def test_explore_shows_only_approved(client: AsyncClient, standard_user_auth_headers: dict, admin_auth_headers: dict):
    project_ids = []
    for i in range(3):
        resp = await client.post(PROJECTS_URL, json={**PROJECT_PAYLOAD, "name": f"Project {i}"}, headers=standard_user_auth_headers)
        project_ids.append(resp.json()["id"])

    await client.patch(f"{ADMIN_PROJECTS_URL}/{project_ids[0]}/approve", headers=admin_auth_headers)
    await client.patch(f"{ADMIN_PROJECTS_URL}/{project_ids[1]}/approve", headers=admin_auth_headers)
    await client.patch(
        f"{ADMIN_PROJECTS_URL}/{project_ids[2]}/reject",
        json={"reason": "Not eligible."},
        headers=admin_auth_headers,
    )

    explore_resp = await client.get(f"{PROJECTS_URL}/explore", headers=standard_user_auth_headers)
    assert explore_resp.json()["total"] == 2



"""
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
