"""
Dealer Services
Business logic for dealer management
"""
from app.core.database import get_service_db
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class DealerService:
    """Service for dealer management operations"""

    @staticmethod
    async def get_all_dealers(status_filter: Optional[str] = None) -> List[dict]:
        """
        Get all dealer accounts

        Args:
            status_filter: Optional filter by dealer_status

        Returns:
            List of dealer profiles
        """
        try:
            supabase = get_service_db()

            query = supabase.table("user_profiles").select("*").eq("user_type", "dealer")

            if status_filter:
                query = query.eq("dealer_status", status_filter)

            response = query.order("created_at", desc=True).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error fetching dealers: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch dealers"
            )

    @staticmethod
    async def get_dealer_by_id(dealer_id: str) -> dict:
        """
        Get dealer details by ID

        Args:
            dealer_id: Dealer user ID

        Returns:
            Dealer profile data
        """
        try:
            supabase = get_service_db()

            response = supabase.table("user_profiles").select("*").eq("id", dealer_id).eq("user_type", "dealer").execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Dealer not found"
                )

            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching dealer {dealer_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch dealer"
            )

    @staticmethod
    async def update_dealer_status(
        dealer_id: str,
        new_status: str,
        notes: str,
        updated_by: str
    ) -> dict:
        """
        Update dealer status

        Args:
            dealer_id: Dealer user ID
            new_status: New dealer status
            notes: Notes about the status change
            updated_by: Staff user ID making the change

        Returns:
            Updated dealer profile
        """
        try:
            supabase = get_service_db()

            # Validate status
            valid_statuses = ["pending", "active", "inactive", "rejected"]
            if new_status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )

            # Update dealer status
            response = supabase.table("user_profiles").update({
                "dealer_status": new_status
            }).eq("id", dealer_id).eq("user_type", "dealer").execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Dealer not found"
                )

            logger.info(f"Dealer {dealer_id} status updated to {new_status} by {updated_by}. Notes: {notes}")

            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating dealer status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update dealer status"
            )

    @staticmethod
    async def get_dealer_orders(dealer_id: str) -> List[dict]:
        """
        Get all orders placed by a dealer

        Args:
            dealer_id: Dealer user ID

        Returns:
            List of orders
        """
        try:
            supabase = get_service_db()

            response = supabase.table("orders").select("*").eq("user_id", dealer_id).order("created_at", desc=True).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error fetching dealer orders: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch dealer orders"
            )
