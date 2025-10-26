"""
Authentication Dependencies
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import get_service_db
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


class CurrentUser(BaseModel):
    """Current authenticated user model"""
    id: str
    email: str
    user_type: str
    first_name: str = ""
    last_name: str = ""
    phone: str = ""


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Dependency to get the current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        CurrentUser: The authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        supabase = get_service_db()

        # Get user from token
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = user_response.user

        # Fetch user profile
        profile_response = supabase.table("user_profiles").select("*").eq("id", user.id).execute()

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        profile = profile_response.data[0]

        return CurrentUser(
            id=user.id,
            email=user.email,
            user_type=profile.get("user_type", "consumer"),
            first_name=profile.get("first_name", ""),
            last_name=profile.get("last_name", ""),
            phone=profile.get("phone", "")
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error getting current user: {error_msg}")

        # Provide more specific error message for common issues
        detail = "Could not validate credentials"
        if "invalid JWT" in error_msg or "token is malformed" in error_msg:
            detail = "Session expired or invalid. Please log in again."
        elif "unable to parse" in error_msg:
            detail = "Invalid authentication token. Please log in again."

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_staff_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency to ensure current user is staff

    Args:
        current_user: The authenticated user

    Returns:
        CurrentUser: The staff user

    Raises:
        HTTPException: If user is not staff
    """
    if current_user.user_type != "staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required"
        )
    return current_user


async def get_current_dealer_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency to ensure current user is a dealer

    Args:
        current_user: The authenticated user

    Returns:
        CurrentUser: The dealer user

    Raises:
        HTTPException: If user is not a dealer
    """
    if current_user.user_type != "dealer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dealer access required"
        )
    return current_user
