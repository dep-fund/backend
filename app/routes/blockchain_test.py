from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.blockchain.contracts.dividends_service import DividendsService
from app.services.blockchain.contracts.dpf_token_service import DpfTokenService
from app.services.blockchain.contracts.offering_service import OfferingService


router = APIRouter(prefix="/test/blockchain", tags=["Blockchain Testing"])


# ─────────────────────────────────────────────
# DPF FACTORY
# ─────────────────────────────────────────────


class CreateTokenRequest(BaseModel):
    name: str
    suffix: str
    supply: int


@router.post("/factory/create-token")
def create_project_token(body: CreateTokenRequest):
    """
    Creates a new DPF token via DpfFactory.
    Uses FACTORY_ADDRESS and MARKETPLACE_ADDRESS from env.
    Returns the address of the deployed token.
    """

    service = DpfTokenService()
    token_address = service.create_project_token(
        body.name,
        body.suffix,
        body.supply,
    )
    return {"token_address": token_address}


# ─────────────────────────────────────────────
# OFFERING
# ─────────────────────────────────────────────


class DeployOfferingRequest(BaseModel):
    dpf_token: str
    soft_cap: int
    hard_cap: int
    token_price: int
    deadline_seconds: int


@router.post("/offering/deploy")
def deploy_offering(body: DeployOfferingRequest):
    """
    Deploys a new Offering contract.
    Uses USDC_ADDRESS and TREASURY_ADDRESS from env.
    Returns the address of the deployed contract.
    """
    try:
        service = OfferingService()
        address = service.deploy(
            body.dpf_token,
            body.soft_cap,
            body.hard_cap,
            body.token_price,
            body.deadline_seconds,
        )
        return {"offering_address": address}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# DIVIDENDS
# ─────────────────────────────────────────────


class DeployDividendsRequest(BaseModel):
    dpf_token: str
    issuer: str
    offering: str


class DistributeRequest(BaseModel):
    dividends_address: str
    usdc_amount: int


@router.post("/dividends/deploy")
def deploy_dividends(body: DeployDividendsRequest):
    """
    Deploys a new Dividends contract.
    Uses USDC_ADDRESS from env.
    Returns the address of the deployed contract.
    """
    try:
        service = DividendsService()
        address = service.deploy(
            body.dpf_token,
            body.issuer,
            body.offering,
        )
        return {"dividends_address": address}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dividends/distribute")
def distribute(body: DistributeRequest):
    """
    Distributes USDC among DPF token holders.
    Only callable by the issuer (deployer).
    """
    try:
        service = DividendsService(address=body.dividends_address)
        receipt = service.distribute(body.usdc_amount)
        return {
            "tx_hash": receipt["transactionHash"].hex(),
            "status": receipt["status"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
