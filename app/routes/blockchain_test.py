from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.blockchain.contracts.dividends_service import DividendsService
from app.services.blockchain.contracts.dpf_token_service import DpfTokenService
from app.services.blockchain.contracts.marketplace_service import MarketplaceService
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


@router.get("/factory/tokens-count")
def tokens_count():
    """
    Returns the total number of tokens created by the factory.
    Uses FACTORY_ADDRESS from env.
    """
    try:
        service = DpfTokenService()
        count = service.tokens_count()
        return {"tokens_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# OFFERING
# ─────────────────────────────────────────────


class DeployOfferingRequest(BaseModel):
    dpf_token: str
    soft_cap: int
    hard_cap: int
    token_price: int
    deadline_seconds: int


class OfferingAddressRequest(BaseModel):
    offering_address: str


class InvestRequest(BaseModel):
    offering_address: str
    usdc_amount: int


class ContributionsRequest(BaseModel):
    offering_address: str
    investor_address: str


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


@router.post("/offering/invest")
def invest(body: InvestRequest):
    """
    Invests USDC into an Offering.
    Uses USDC_ADDRESS from env for approval context.
    """
    try:
        service = OfferingService(address=body.offering_address)
        receipt = service.invest(body.usdc_amount)
        return {
            "tx_hash": receipt["transactionHash"].hex(),
            "status": receipt["status"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/offering/refund")
def refund(body: OfferingAddressRequest):
    """
    Requests a refund from an Offering that did not reach the soft cap.
    """
    try:
        service = OfferingService(address=body.offering_address)
        receipt = service.refund()
        return {
            "tx_hash": receipt["transactionHash"].hex(),
            "status": receipt["status"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/offering/withdraw")
def withdraw(body: OfferingAddressRequest):
    """
    Withdraws raised funds from an Offering that reached the soft cap.
    Only callable by the issuer (deployer).
    """
    try:
        service = OfferingService(address=body.offering_address)
        receipt = service.withdraw()
        return {
            "tx_hash": receipt["transactionHash"].hex(),
            "status": receipt["status"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/offering/status")
def offering_status(offering_address: str):
    """
    Returns the current state of an Offering: total raised, soft cap.
    Useful to verify that invest/withdraw/refund worked correctly.
    """
    try:
        service = OfferingService(address=offering_address)
        total_raised = service.total_raised()
        soft_cap = service.soft_cap()
        return {
            "offering_address": offering_address,
            "total_raised": total_raised,
            "soft_cap": soft_cap,
            "soft_cap_reached": total_raised >= soft_cap,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/offering/contributions")
def contributions(offering_address: str, investor_address: str):
    """
    Returns the USDC contributed by a specific investor in an Offering.
    """
    try:
        service = OfferingService(address=offering_address)
        amount = service.contributions(investor_address)
        return {
            "investor": investor_address,
            "contributed_usdc": amount,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# DIVIDENDS
# ─────────────────────────────────────────────


class DeployDividendsRequest(BaseModel):
    dpf_token: str
    issuer: str
    offering: str


class DividendsAddressRequest(BaseModel):
    dividends_address: str


class DistributeRequest(BaseModel):
    dividends_address: str
    usdc_amount: int


class PendingRequest(BaseModel):
    dividends_address: str
    holder: str


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


@router.get("/dividends/pending")
def pending(dividends_address: str, holder: str):
    """
    Returns the pending USDC dividends for a holder.
    """
    try:
        service = DividendsService(address=dividends_address)
        amount = service.pending(holder)
        return {
            "holder": holder,
            "pending_usdc": amount,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dividends/claim")
def claim(body: DividendsAddressRequest):
    """
    Claims pending dividends for the deployer account.
    """
    try:
        service = DividendsService(address=body.dividends_address)
        receipt = service.claim()
        return {
            "tx_hash": receipt["transactionHash"].hex(),
            "status": receipt["status"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# MARKETPLACE
# ─────────────────────────────────────────────


class ListTokenRequest(BaseModel):
    token: str
    amount: int
    price_usdc: int


class ListingIdRequest(BaseModel):
    listing_id: int


@router.post("/marketplace/list")
def list_token(body: ListTokenRequest):
    """
    Publishes a sell offer on the Marketplace.
    Uses MARKETPLACE_ADDRESS from env.
    Returns the listing ID.
    """
    try:
        service = MarketplaceService()
        listing_id = service.list_token(body.token, body.amount, body.price_usdc)
        return {"listing_id": listing_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/marketplace/buy")
def buy(body: ListingIdRequest):
    """
    Purchases an active listing.
    Uses MARKETPLACE_ADDRESS from env.
    """
    try:
        service = MarketplaceService()
        receipt = service.buy(body.listing_id)
        return {
            "tx_hash": receipt["transactionHash"].hex(),
            "status": receipt["status"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/marketplace/cancel")
def cancel(body: ListingIdRequest):
    """
    Cancels an active listing and returns the tokens to the seller.
    Uses MARKETPLACE_ADDRESS from env.
    """
    try:
        service = MarketplaceService()
        receipt = service.cancel(body.listing_id)
        return {
            "tx_hash": receipt["transactionHash"].hex(),
            "status": receipt["status"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace/listing")
def get_listing(listing_id: int):
    """
    Returns the details of a listing by ID.
    Uses MARKETPLACE_ADDRESS from env.
    """
    try:
        service = MarketplaceService()
        listing = service.get_listing(listing_id)
        return listing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/marketplace/listings-count")
def listings_count():
    """
    Returns the total number of listings created on the Marketplace.
    Uses MARKETPLACE_ADDRESS from env.
    """
    try:
        service = MarketplaceService()
        count = service.listings_count()
        return {"listings_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
