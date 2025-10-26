"""
Customer Services
Business logic for customer management
"""
from app.core.database import get_service_db
from fastapi import HTTPException, status
from typing import List
import logging

logger = logging.getLogger(__name__)


class CustomerService:
    """Service for customer management operations"""

    @staticmethod
    async def get_all_customers() -> List[dict]:
        """
        Get all consumer accounts

        Returns:
            List of consumer profiles
        """
        try:
            supabase = get_service_db()

            response = supabase.table("user_profiles").select("*").eq("user_type", "consumer").order("created_at", desc=True).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error fetching customers: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch customers"
            )

    @staticmethod
    async def get_customer_by_id(customer_id: str) -> dict:
        """
        Get customer details by ID

        Args:
            customer_id: Customer user ID

        Returns:
            Customer profile data
        """
        try:
            supabase = get_service_db()

            response = supabase.table("user_profiles").select("*").eq("id", customer_id).eq("user_type", "consumer").execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found"
                )

            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching customer {customer_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch customer"
            )

    @staticmethod
    async def get_customer_orders(customer_id: str) -> List[dict]:
        """
        Get all orders placed by a customer

        Args:
            customer_id: Customer user ID

        Returns:
            List of orders
        """
        try:
            supabase = get_service_db()

            response = supabase.table("orders").select("*").eq("user_id", customer_id).order("created_at", desc=True).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error fetching customer orders: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch customer orders"
            )
