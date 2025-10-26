"""
Category Routes
API endpoints for category management
"""
from fastapi import APIRouter, HTTPException, status, Query
from app.functions.categories.models import (
    Category,
    CategoryCreate,
    CategoryUpdate,
    CategoryTree
)
from app.functions.categories.services import CategoryService
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.get(
    "/",
    response_model=List[Category],
    summary="Get all categories"
)
async def get_categories(
    include_inactive: bool = Query(False, description="Include inactive categories")
):
    """
    Get all categories (flat list)

    - **include_inactive**: Set to true to include inactive categories (default: false)
    """
    categories = await CategoryService.get_all_categories(include_inactive=include_inactive)
    return categories


@router.get(
    "/tree",
    summary="Get category tree",
    description="Get categories as a hierarchical tree structure"
)
async def get_category_tree():
    """
    Get categories organized in a hierarchical tree structure

    Returns categories with nested children for easy navigation.
    """
    tree = await CategoryService.get_category_tree()
    return {"categories": tree}


@router.get(
    "/{category_id}",
    response_model=Category,
    summary="Get category by ID"
)
async def get_category(category_id: str):
    """
    Get a specific category by ID

    - **category_id**: UUID of the category
    """
    category = await CategoryService.get_category_by_id(category_id)
    return category


@router.get(
    "/slug/{slug}",
    response_model=Category,
    summary="Get category by slug"
)
async def get_category_by_slug(slug: str):
    """
    Get a specific category by slug

    - **slug**: URL-friendly category identifier (e.g., 'submersible-pumps')
    """
    category = await CategoryService.get_category_by_slug(slug)
    return category


@router.post(
    "/",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category"
)
async def create_category(category_data: CategoryCreate):
    """
    Create a new category

    - **name**: Category name (required)
    - **slug**: URL-friendly identifier (required, must be unique)
    - **description**: Optional description
    - **parent_id**: UUID of parent category for nested categories
    - **sort_order**: Display order (default: 0)
    - **is_active**: Active status (default: true)
    - **metadata**: Additional custom data as JSON

    **Note:** Requires staff permissions
    """
    category = await CategoryService.create_category(category_data)
    return category


@router.put(
    "/{category_id}",
    response_model=Category,
    summary="Update a category"
)
async def update_category(category_id: str, category_data: CategoryUpdate):
    """
    Update an existing category

    - **category_id**: UUID of the category to update
    - All fields are optional - only provide fields you want to update

    **Note:** Requires staff permissions
    """
    category = await CategoryService.update_category(category_id, category_data)
    return category


@router.delete(
    "/{category_id}",
    summary="Delete a category"
)
async def delete_category(category_id: str):
    """
    Delete a category (soft delete - sets is_active to false)

    - **category_id**: UUID of the category to delete

    **Note:**
    - Cannot delete categories with child categories
    - Cannot delete categories with products
    - Requires staff permissions
    """
    result = await CategoryService.delete_category(category_id)
    return result
