"""
Dealer Routes
API endpoints for dealer management (staff only)
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.functions.dealers.services import DealerService
from app.functions.auth.dependencies import get_current_staff_user
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dealers", tags=["Dealers"])


class DealerStatusUpdate(BaseModel):
    dealer_status: str
    notes: str = ""


@router.get(
    "/",
    summary="Get all dealers (Staff only)"
)
async def get_all_dealers(
    status_filter: str = None,
    current_user = Depends(get_current_staff_user)
):
    """
    Get all dealer accounts

    - **status_filter**: Optional filter by dealer status (pending, active, inactive, rejected)

    Requires staff authentication.
    """
    result = await DealerService.get_all_dealers(status_filter=status_filter)
    return result


@router.get(
    "/{dealer_id}",
    summary="Get dealer by ID (Staff only)"
)
async def get_dealer(
    dealer_id: str,
    current_user = Depends(get_current_staff_user)
):
    """
    Get dealer details by ID

    Requires staff authentication.
    """
    result = await DealerService.get_dealer_by_id(dealer_id)
    return result


@router.put(
    "/{dealer_id}/status",
    summary="Update dealer status (Staff only)"
)
async def update_dealer_status(
    dealer_id: str,
    status_update: DealerStatusUpdate,
    current_user = Depends(get_current_staff_user)
):
    """
    Update dealer account status

    - **dealer_status**: New status (pending, active, inactive, rejected)
    - **notes**: Optional notes about the status change

    Requires staff authentication.
    """
    result = await DealerService.update_dealer_status(
        dealer_id,
        status_update.dealer_status,
        status_update.notes,
        current_user.id
    )
    return result


@router.get(
    "/{dealer_id}/orders",
    summary="Get dealer orders (Staff only)"
)
async def get_dealer_orders(
    dealer_id: str,
    current_user = Depends(get_current_staff_user)
):
    """
    Get all orders placed by a dealer

    Requires staff authentication.
    """
    result = await DealerService.get_dealer_orders(dealer_id)
    return result
