"""
Order Routes
API endpoints for order management
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.functions.orders.models import OrderCreate, OrderResponse
from app.functions.orders.services import OrderService
from app.functions.auth.dependencies import get_current_user, get_current_staff_user
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


class OrderStatusUpdate(BaseModel):
    status: str
    notes: str = ""


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order"
)
async def create_order(order_data: OrderCreate):
    """
    Create a new order (guest or authenticated)

    **Guest Checkout:**
    - Provide customer details and shipping address
    - Optionally create account by setting `create_account: true` and providing `account_password`

    **Order Fields:**
    - **customer_email**: Customer email (required)
    - **customer_first_name**: First name (required)
    - **customer_last_name**: Last name (required)
    - **customer_phone**: Phone number (optional)
    - **shipping_address_line1**: Street address (required)
    - **shipping_city**: City (required)
    - **shipping_state**: State (required)
    - **shipping_postal_code**: Postal/ZIP code (required)
    - **items**: Array of order items (required)
    - **create_account**: Set to true to create account (optional)
    - **account_password**: Password for new account (required if create_account is true)

    **Response:**
    - Returns order details, items, and account creation status
    """
    result = await OrderService.create_order(order_data)
    return OrderResponse(**result)


@router.get(
    "/{order_id}",
    summary="Get order by ID"
)
async def get_order(order_id: str):
    """
    Get order details by ID

    - **order_id**: UUID of the order
    """
    result = await OrderService.get_order_by_id(order_id)
    return result


@router.get(
    "/number/{order_number}",
    summary="Get order by order number"
)
async def get_order_by_number(order_number: str):
    """
    Get order details by order number

    - **order_number**: Order number (e.g., JOV-20250126-001)
    """
    result = await OrderService.get_order_by_number(order_number)
    return result


@router.get(
    "/user/me",
    summary="Get current user's orders"
)
async def get_my_orders(current_user = Depends(get_current_user)):
    """
    Get all orders for the currently authenticated user

    Requires authentication. Returns orders sorted by creation date (newest first).
    """
    result = await OrderService.get_user_orders(current_user.id)
    return result


@router.get(
    "/staff/all",
    summary="Get all orders (Staff only)"
)
async def get_all_orders(
    status: str = None,
    current_user = Depends(get_current_staff_user)
):
    """
    Get all orders for staff management

    - **status**: Optional filter by order status

    Requires staff authentication. Returns all orders sorted by creation date (newest first).
    """
    result = await OrderService.get_all_orders(status_filter=status)
    return result


@router.put(
    "/{order_id}/status",
    summary="Update order status (Staff only)"
)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user = Depends(get_current_staff_user)
):
    """
    Update order status

    - **order_id**: UUID of the order
    - **status**: New status (pending, processing, shipped, delivered, cancelled)
    - **notes**: Optional notes about the status change

    Requires staff authentication.
    """
    result = await OrderService.update_order_status(
        order_id,
        status_update.status,
        status_update.notes,
        current_user.id
    )
    return result
