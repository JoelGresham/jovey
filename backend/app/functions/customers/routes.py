"""
Customer Routes
API endpoints for customer management (staff only)
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.functions.customers.services import CustomerService
from app.functions.auth.dependencies import get_current_staff_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.get(
    "/",
    summary="Get all customers (Staff only)"
)
async def get_all_customers(
    current_user = Depends(get_current_staff_user)
):
    """
    Get all consumer accounts

    Requires staff authentication.
    """
    result = await CustomerService.get_all_customers()
    return result


@router.get(
    "/{customer_id}",
    summary="Get customer by ID (Staff only)"
)
async def get_customer(
    customer_id: str,
    current_user = Depends(get_current_staff_user)
):
    """
    Get customer details by ID

    Requires staff authentication.
    """
    result = await CustomerService.get_customer_by_id(customer_id)
    return result


@router.get(
    "/{customer_id}/orders",
    summary="Get customer orders (Staff only)"
)
async def get_customer_orders(
    customer_id: str,
    current_user = Depends(get_current_staff_user)
):
    """
    Get all orders placed by a customer

    Requires staff authentication.
    """
    result = await CustomerService.get_customer_orders(customer_id)
    return result
