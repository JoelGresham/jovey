"""
Authentication Services
Business logic for authentication operations
"""
from app.core.database import get_service_db
from app.functions.auth.models import UserRegisterRequest, UserProfile
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management"""

    @staticmethod
    async def register_user(user_data: UserRegisterRequest) -> dict:
        """
        Register a new user with Supabase Auth and create profile

        Args:
            user_data: User registration data

        Returns:
            dict: Supabase auth response with user and session

        Raises:
            HTTPException: If registration fails
        """
        try:
            supabase = get_service_db()

            # Register user with Supabase Auth
            logger.info(f"Attempting to register user: {user_data.email}")
            auth_response = supabase.auth.sign_up(
                credentials={
                    "email": user_data.email,
                    "password": user_data.password
                }
            )

            logger.info(f"Auth response: {auth_response}")

            if not auth_response.user:
                error_msg = "Failed to create user account"
                if hasattr(auth_response, 'error') and auth_response.error:
                    error_msg = f"Failed to create user account: {auth_response.error}"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )

            user_id = auth_response.user.id
            logger.info(f"User created in Supabase Auth with ID: {user_id}")

            # Create user profile
            profile_data = {
                "id": user_id,
                "email": user_data.email,
                "user_type": user_data.user_type,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "phone": user_data.phone,
            }

            # Add dealer-specific fields
            if user_data.user_type == "dealer":
                profile_data["company_name"] = user_data.company_name
                profile_data["dealer_status"] = "pending"  # Requires approval

            # Insert profile
            profile_response = supabase.table("user_profiles").insert(profile_data).execute()

            if not profile_response.data:
                # Rollback: delete auth user if profile creation fails
                logger.error(f"Failed to create profile for user {user_id}")
                # Note: In production, implement proper cleanup
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user profile"
                )

            logger.info(f"User registered successfully: {user_data.email} (type: {user_data.user_type})")

            return {
                "user": auth_response.user,
                "session": auth_response.session,
                "profile": profile_response.data[0]
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )

    @staticmethod
    async def login_user(email: str, password: str) -> dict:
        """
        Authenticate user with email and password

        Args:
            email: User email
            password: User password

        Returns:
            dict: Supabase auth response with user, session, and profile

        Raises:
            HTTPException: If authentication fails
        """
        try:
            supabase = get_service_db()

            # Authenticate with Supabase
            auth_response = supabase.auth.sign_in_with_password(
                credentials={
                    "email": email,
                    "password": password
                }
            )

            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            user_id = auth_response.user.id

            # Fetch user profile
            profile_response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()

            if not profile_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )

            profile = profile_response.data[0]

            # Check dealer status
            if profile["user_type"] == "dealer" and profile.get("dealer_status") != "active":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Dealer account is {profile.get('dealer_status', 'pending')}. Please wait for approval."
                )

            logger.info(f"User logged in: {email}")

            return {
                "user": auth_response.user,
                "session": auth_response.session,
                "profile": profile
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )

    @staticmethod
    async def get_user_profile(user_id: str) -> dict:
        """
        Get user profile by user ID

        Args:
            user_id: User ID

        Returns:
            dict: User profile data
        """
        try:
            supabase = get_service_db()

            response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )

            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user profile"
            )

    @staticmethod
    async def update_profile(user_id: str, profile_data: dict) -> dict:
        """
        Update user profile

        Args:
            user_id: User ID
            profile_data: Updated profile data

        Returns:
            dict: Updated user profile
        """
        try:
            supabase = get_service_db()

            # Update profile
            response = supabase.table("user_profiles").update(profile_data).eq("id", user_id).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )

            logger.info(f"Profile updated for user: {user_id}")
            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )

    @staticmethod
    async def change_password(email: str, current_password: str, new_password: str):
        """
        Change user password

        Args:
            email: User email
            current_password: Current password
            new_password: New password

        Raises:
            HTTPException: If password change fails
        """
        try:
            supabase = get_service_db()

            # Verify current password
            try:
                auth_response = supabase.auth.sign_in_with_password(
                    credentials={
                        "email": email,
                        "password": current_password
                    }
                )
                if not auth_response.user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Current password is incorrect"
                    )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current password is incorrect"
                )

            # Update password
            update_response = supabase.auth.update_user(
                attributes={"password": new_password}
            )

            if not update_response.user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update password"
                )

            logger.info(f"Password changed for user: {email}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password"
            )
