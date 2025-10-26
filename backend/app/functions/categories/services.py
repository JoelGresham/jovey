"""
Category Services
Business logic for category management
"""
from app.core.database import get_service_db
from app.functions.categories.models import CategoryCreate, CategoryUpdate
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class CategoryService:
    """Service for category operations"""

    @staticmethod
    async def get_all_categories(include_inactive: bool = False) -> List[dict]:
        """
        Get all categories

        Args:
            include_inactive: Include inactive categories

        Returns:
            List of category dictionaries
        """
        try:
            supabase = get_service_db()
            query = supabase.table("categories").select("*").order("sort_order", desc=False)

            if not include_inactive:
                query = query.eq("is_active", True)

            response = query.execute()
            return response.data

        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch categories"
            )

    @staticmethod
    async def get_category_tree() -> List[dict]:
        """
        Get categories as a hierarchical tree

        Returns:
            List of top-level categories with nested children
        """
        try:
            categories = await CategoryService.get_all_categories()

            # Build tree structure
            category_map = {cat['id']: {**cat, 'children': []} for cat in categories}

            tree = []
            for category in categories:
                if category['parent_id']:
                    parent = category_map.get(category['parent_id'])
                    if parent:
                        parent['children'].append(category_map[category['id']])
                else:
                    tree.append(category_map[category['id']])

            return tree

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error building category tree: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to build category tree"
            )

    @staticmethod
    async def get_category_by_id(category_id: str) -> dict:
        """
        Get a category by ID

        Args:
            category_id: Category UUID

        Returns:
            Category dictionary

        Raises:
            HTTPException: If category not found
        """
        try:
            supabase = get_service_db()
            response = supabase.table("categories").select("*").eq("id", category_id).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )

            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching category {category_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch category"
            )

    @staticmethod
    async def get_category_by_slug(slug: str) -> dict:
        """
        Get a category by slug

        Args:
            slug: Category slug

        Returns:
            Category dictionary

        Raises:
            HTTPException: If category not found
        """
        try:
            supabase = get_service_db()
            response = supabase.table("categories").select("*").eq("slug", slug).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )

            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching category by slug {slug}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch category"
            )

    @staticmethod
    async def create_category(category_data: CategoryCreate) -> dict:
        """
        Create a new category

        Args:
            category_data: Category creation data

        Returns:
            Created category dictionary

        Raises:
            HTTPException: If creation fails
        """
        try:
            supabase = get_service_db()

            # Check if slug already exists
            existing = supabase.table("categories").select("id").eq("slug", category_data.slug).execute()
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with slug '{category_data.slug}' already exists"
                )

            # Check if parent exists (if provided)
            if category_data.parent_id:
                parent_response = supabase.table("categories").select("id").eq("id", str(category_data.parent_id)).execute()
                if not parent_response.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Parent category not found"
                    )

            # Create category
            response = supabase.table("categories").insert(category_data.model_dump()).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create category"
                )

            logger.info(f"Category created: {category_data.name} ({category_data.slug})")
            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create category: {str(e)}"
            )

    @staticmethod
    async def update_category(category_id: str, category_data: CategoryUpdate) -> dict:
        """
        Update a category

        Args:
            category_id: Category UUID
            category_data: Category update data

        Returns:
            Updated category dictionary

        Raises:
            HTTPException: If update fails
        """
        try:
            supabase = get_service_db()

            # Check if category exists
            await CategoryService.get_category_by_id(category_id)

            # Check if new slug already exists (if slug is being updated)
            if category_data.slug:
                existing = supabase.table("categories").select("id").eq("slug", category_data.slug).neq("id", category_id).execute()
                if existing.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Category with slug '{category_data.slug}' already exists"
                    )

            # Update category
            update_data = category_data.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No update data provided"
                )

            response = supabase.table("categories").update(update_data).eq("id", category_id).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update category"
                )

            logger.info(f"Category updated: {category_id}")
            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating category {category_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update category: {str(e)}"
            )

    @staticmethod
    async def delete_category(category_id: str) -> dict:
        """
        Delete a category (soft delete by setting is_active=False)

        Args:
            category_id: Category UUID

        Returns:
            Success message

        Raises:
            HTTPException: If deletion fails
        """
        try:
            supabase = get_service_db()

            # Check if category exists
            await CategoryService.get_category_by_id(category_id)

            # Check if category has children
            children = supabase.table("categories").select("id").eq("parent_id", category_id).execute()
            if children.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete category with child categories"
                )

            # Check if category has products
            products = supabase.table("products").select("id").eq("category_id", category_id).execute()
            if products.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete category with products. Please reassign products first."
                )

            # Soft delete (set is_active to False)
            response = supabase.table("categories").update({"is_active": False}).eq("id", category_id).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete category"
                )

            logger.info(f"Category deleted (soft): {category_id}")
            return {"message": "Category deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting category {category_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete category: {str(e)}"
            )
