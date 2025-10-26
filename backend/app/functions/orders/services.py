"""
Order Services
Business logic for order management
"""
from app.core.database import get_service_db
from app.functions.orders.models import OrderCreate
from app.functions.auth.models import UserRegisterRequest
from app.functions.auth.services import AuthService
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order operations"""

    @staticmethod
    async def create_order(order_data: OrderCreate, user_id: Optional[str] = None) -> dict:
        """
        Create a new order (guest or authenticated)

        Args:
            order_data: Order creation data
            user_id: Optional user ID if authenticated

        Returns:
            dict with order, items, and account creation status

        Raises:
            HTTPException: If order creation fails
        """
        try:
            supabase = get_service_db()
            account_created = False
            new_user_id = user_id

            # If guest wants to create account
            if order_data.create_account and not user_id:
                if not order_data.account_password:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Password required to create account"
                    )

                try:
                    # Create user account
                    user_request = UserRegisterRequest(
                        email=order_data.customer_email,
                        password=order_data.account_password,
                        first_name=order_data.customer_first_name,
                        last_name=order_data.customer_last_name,
                        phone=order_data.customer_phone or "",
                        user_type="consumer"
                    )

                    user_result = await AuthService.register_user(user_request)
                    new_user_id = user_result["user"].id
                    account_created = True
                    logger.info(f"Account created for {order_data.customer_email} during checkout")
                except Exception as e:
                    # If account creation fails, continue with guest order
                    logger.warning(f"Failed to create account during checkout: {str(e)}")

            # Create order
            order_dict = {
                "user_id": new_user_id,
                "customer_email": order_data.customer_email,
                "customer_first_name": order_data.customer_first_name,
                "customer_last_name": order_data.customer_last_name,
                "customer_phone": order_data.customer_phone,
                "shipping_address_line1": order_data.shipping_address_line1,
                "shipping_address_line2": order_data.shipping_address_line2,
                "shipping_city": order_data.shipping_city,
                "shipping_state": order_data.shipping_state,
                "shipping_postal_code": order_data.shipping_postal_code,
                "shipping_country": order_data.shipping_country,
                "billing_address_line1": order_data.billing_address_line1,
                "billing_address_line2": order_data.billing_address_line2,
                "billing_city": order_data.billing_city,
                "billing_state": order_data.billing_state,
                "billing_postal_code": order_data.billing_postal_code,
                "billing_country": order_data.billing_country,
                "subtotal": float(order_data.subtotal),
                "shipping_cost": float(order_data.shipping_cost),
                "tax_amount": float(order_data.tax_amount),
                "total_amount": float(order_data.total_amount),
                "customer_notes": order_data.customer_notes,
                "status": "pending",
                "payment_status": "pending"
            }

            order_response = supabase.table("orders").insert(order_dict).execute()

            if not order_response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create order"
                )

            order = order_response.data[0]
            order_id = order["id"]

            # Create order items
            items = []
            for item in order_data.items:
                item_dict = {
                    "order_id": order_id,
                    "product_id": str(item.product_id),
                    "product_name": item.product_name,
                    "product_sku": item.product_sku,
                    "product_slug": item.product_slug,
                    "unit_price": float(item.unit_price),
                    "quantity": item.quantity,
                    "subtotal": float(item.subtotal),
                    "specifications": item.specifications
                }

                item_response = supabase.table("order_items").insert(item_dict).execute()

                if item_response.data:
                    items.append(item_response.data[0])

            # Create initial status history
            supabase.table("order_status_history").insert({
                "order_id": order_id,
                "status": "pending",
                "notes": "Order created",
                "created_by": new_user_id
            }).execute()

            logger.info(f"Order created: {order['order_number']} for {order_data.customer_email}")

            return {
                "order": order,
                "items": items,
                "account_created": account_created,
                "message": "Order created successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create order: {str(e)}"
            )

    @staticmethod
    async def get_order_by_id(order_id: str) -> dict:
        """Get order with items by ID"""
        try:
            supabase = get_service_db()

            # Get order
            order_response = supabase.table("orders").select("*").eq("id", order_id).execute()

            if not order_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found"
                )

            order = order_response.data[0]

            # Get order items
            items_response = supabase.table("order_items").select("*").eq("order_id", order_id).execute()
            items = items_response.data if items_response.data else []

            return {
                "order": order,
                "items": items
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch order"
            )

    @staticmethod
    async def get_order_by_number(order_number: str) -> dict:
        """Get order with items by order number"""
        try:
            supabase = get_service_db()

            # Get order
            order_response = supabase.table("orders").select("*").eq("order_number", order_number).execute()

            if not order_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found"
                )

            order = order_response.data[0]

            # Get order items
            items_response = supabase.table("order_items").select("*").eq("order_id", order["id"]).execute()
            items = items_response.data if items_response.data else []

            return {
                "order": order,
                "items": items
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching order {order_number}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch order"
            )

    @staticmethod
    async def get_user_orders(user_id: str) -> List[dict]:
        """Get all orders for a user"""
        try:
            supabase = get_service_db()

            response = supabase.table("orders_summary").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error fetching user orders: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch orders"
            )

    @staticmethod
    async def get_all_orders(status_filter: Optional[str] = None) -> List[dict]:
        """Get all orders (staff only)"""
        try:
            supabase = get_service_db()

            query = supabase.table("orders").select("*")

            if status_filter:
                query = query.eq("status", status_filter)

            response = query.order("created_at", desc=True).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error fetching all orders: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch orders"
            )

    @staticmethod
    async def update_order_status(
        order_id: str,
        new_status: str,
        notes: str,
        updated_by: str
    ) -> dict:
        """Update order status (staff only)"""
        try:
            supabase = get_service_db()

            # Validate status
            valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
            if new_status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )

            # Update order
            order_response = supabase.table("orders").update({
                "status": new_status
            }).eq("id", order_id).execute()

            if not order_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found"
                )

            # Add status history
            supabase.table("order_status_history").insert({
                "order_id": order_id,
                "status": new_status,
                "notes": notes,
                "created_by": updated_by
            }).execute()

            logger.info(f"Order {order_id} status updated to {new_status} by {updated_by}")

            return order_response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update order status"
            )
