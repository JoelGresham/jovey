"""
Authentication Routes
API endpoints for authentication operations
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.functions.auth.models import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    UserProfile,
    ErrorResponse
)
from app.functions.auth.services import AuthService
from app.functions.auth.dependencies import get_current_user
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class ProfileUpdateRequest(BaseModel):
    first_name: str
    last_name: str
    phone: str = ""


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def register(user_data: UserRegisterRequest):
    """
    Register a new user

    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **user_type**: Must be 'consumer', 'dealer', or 'staff'
    - **first_name**: Optional
    - **last_name**: Optional
    - **phone**: Optional
    - **company_name**: Required for dealers

    Returns authentication token and user profile.
    """
    try:
        # Validate user type
        if user_data.user_type not in ["consumer", "dealer", "staff"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_type must be 'consumer', 'dealer', or 'staff'"
            )

        # Validate dealer requires company name
        if user_data.user_type == "dealer" and not user_data.company_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="company_name is required for dealer accounts"
            )

        # Register user
        result = await AuthService.register_user(user_data)

        # Format response
        user_profile = UserProfile(**result["profile"])

        # Check if session exists (email confirmation might be required)
        if result["session"] is None:
            # Email confirmation required
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail="Registration successful! Please check your email to confirm your account before logging in."
            )

        return AuthResponse(
            access_token=result["session"].access_token,
            token_type="bearer",
            user=user_profile,
            expires_in=result["session"].expires_in or 3600
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        403: {"model": ErrorResponse, "description": "Account not active"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def login(credentials: UserLoginRequest):
    """
    Authenticate user with email and password

    - **email**: User's email address
    - **password**: User's password

    Returns authentication token and user profile.
    """
    try:
        # Authenticate user
        result = await AuthService.login_user(
            credentials.email,
            credentials.password
        )

        # Format response
        user_profile = UserProfile(**result["profile"])

        return AuthResponse(
            access_token=result["session"].access_token,
            token_type="bearer",
            user=user_profile,
            expires_in=result["session"].expires_in or 3600
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get(
    "/me",
    response_model=UserProfile,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
async def get_current_user():
    """
    Get current authenticated user profile

    Requires valid authentication token in Authorization header.
    """
    # TODO: Implement token verification and user extraction
    # For now, return placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token verification not yet implemented. Use /login to get user info."
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def logout():
    """
    Logout current user

    Invalidates the current session token.
    """
    # TODO: Implement token invalidation
    return {"message": "Logout successful"}


@router.put(
    "/profile",
    response_model=UserProfile,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        400: {"model": ErrorResponse, "description": "Invalid data"}
    }
)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user = Depends(get_current_user)
):
    """
    Update current user's profile

    - **first_name**: User's first name
    - **last_name**: User's last name
    - **phone**: User's phone number (optional)

    Requires authentication.
    """
    try:
        result = await AuthService.update_profile(
            current_user.id,
            profile_data.dict()
        )
        return UserProfile(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        400: {"model": ErrorResponse, "description": "Invalid password"}
    }
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user = Depends(get_current_user)
):
    """
    Change current user's password

    - **current_password**: User's current password
    - **new_password**: New password (minimum 8 characters)

    Requires authentication.
    """
    try:
        # Validate new password length
        if len(password_data.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters"
            )

        await AuthService.change_password(
            current_user.email,
            password_data.current_password,
            password_data.new_password
        )

        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
