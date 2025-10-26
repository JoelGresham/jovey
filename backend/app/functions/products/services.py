"""
Product Services
Business logic for product management
"""
from app.core.database import get_service_db
from app.functions.products.models import ProductCreate, ProductUpdate
from fastapi import HTTPException, status, UploadFile
from typing import List, Optional
import logging
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class ProductService:
    """Service for product operations"""

    @staticmethod
    async def get_all_products(
        include_inactive: bool = False,
        category_id: Optional[str] = None,
        search: Optional[str] = None,
        is_featured: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """
        Get all products with optional filtering

        Args:
            include_inactive: Include inactive products
            category_id: Filter by category UUID
            search: Search in name and description
            is_featured: Filter featured products
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            List of product dictionaries
        """
        try:
            supabase = get_service_db()
            query = supabase.table("products_with_category").select("*")

            if not include_inactive:
                query = query.eq("is_active", True)

            if category_id:
                query = query.eq("category_id", category_id)

            if is_featured is not None:
                query = query.eq("is_featured", is_featured)

            if search:
                query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")

            query = query.order("sort_order", desc=False).order("created_at", desc=True)
            query = query.range(offset, offset + limit - 1)

            response = query.execute()
            return response.data

        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch products"
            )

    @staticmethod
    async def get_product_by_id(product_id: str) -> dict:
        """
        Get a product by ID

        Args:
            product_id: Product UUID

        Returns:
            Product dictionary

        Raises:
            HTTPException: If product not found
        """
        try:
            supabase = get_service_db()
            response = supabase.table("products_with_category").select("*").eq("id", product_id).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )

            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch product"
            )

    @staticmethod
    async def get_product_by_slug(slug: str) -> dict:
        """
        Get a product by slug

        Args:
            slug: Product slug

        Returns:
            Product dictionary

        Raises:
            HTTPException: If product not found
        """
        try:
            supabase = get_service_db()
            response = supabase.table("products_with_category").select("*").eq("slug", slug).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )

            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching product by slug {slug}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch product"
            )

    @staticmethod
    async def create_product(product_data: ProductCreate, user_id: Optional[str] = None) -> dict:
        """
        Create a new product

        Args:
            product_data: Product creation data
            user_id: ID of user creating the product

        Returns:
            Created product dictionary

        Raises:
            HTTPException: If creation fails
        """
        try:
            supabase = get_service_db()

            # Check if slug already exists
            existing = supabase.table("products").select("id").eq("slug", product_data.slug).execute()
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with slug '{product_data.slug}' already exists"
                )

            # Check if SKU already exists (if provided)
            if product_data.sku:
                existing_sku = supabase.table("products").select("id").eq("sku", product_data.sku).execute()
                if existing_sku.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Product with SKU '{product_data.sku}' already exists"
                    )

            # Check if category exists (if provided)
            if product_data.category_id:
                category_response = supabase.table("categories").select("id").eq("id", str(product_data.category_id)).execute()
                if not category_response.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Category not found"
                    )

            # Create product
            product_dict = product_data.model_dump()
            if user_id:
                product_dict["created_by"] = user_id

            response = supabase.table("products").insert(product_dict).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create product"
                )

            logger.info(f"Product created: {product_data.name} ({product_data.slug})")
            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create product: {str(e)}"
            )

    @staticmethod
    async def update_product(product_id: str, product_data: ProductUpdate) -> dict:
        """
        Update a product

        Args:
            product_id: Product UUID
            product_data: Product update data

        Returns:
            Updated product dictionary

        Raises:
            HTTPException: If update fails
        """
        try:
            supabase = get_service_db()

            # Check if product exists
            await ProductService.get_product_by_id(product_id)

            # Check if new slug already exists (if slug is being updated)
            if product_data.slug:
                existing = supabase.table("products").select("id").eq("slug", product_data.slug).neq("id", product_id).execute()
                if existing.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Product with slug '{product_data.slug}' already exists"
                    )

            # Check if new SKU already exists (if SKU is being updated)
            if product_data.sku:
                existing_sku = supabase.table("products").select("id").eq("sku", product_data.sku).neq("id", product_id).execute()
                if existing_sku.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Product with SKU '{product_data.sku}' already exists"
                    )

            # Update product
            update_data = product_data.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No update data provided"
                )

            response = supabase.table("products").update(update_data).eq("id", product_id).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update product"
                )

            logger.info(f"Product updated: {product_id}")
            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update product: {str(e)}"
            )

    @staticmethod
    async def delete_product(product_id: str) -> dict:
        """
        Delete a product (soft delete by setting is_active=False)

        Args:
            product_id: Product UUID

        Returns:
            Success message

        Raises:
            HTTPException: If deletion fails
        """
        try:
            supabase = get_service_db()

            # Check if product exists
            await ProductService.get_product_by_id(product_id)

            # Soft delete (set is_active to False)
            response = supabase.table("products").update({"is_active": False}).eq("id", product_id).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete product"
                )

            logger.info(f"Product deleted (soft): {product_id}")
            return {"message": "Product deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete product: {str(e)}"
            )

    @staticmethod
    async def upload_product_image(file: UploadFile) -> str:
        """
        Upload a product image to Supabase storage

        Args:
            file: The uploaded image file

        Returns:
            Public URL of the uploaded image

        Raises:
            ValueError: If file type is invalid
            HTTPException: If upload fails
        """
        try:
            # Validate file type
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
            if file.content_type not in allowed_types:
                raise ValueError(
                    f"Invalid file type: {file.content_type}. "
                    f"Allowed types: {', '.join(allowed_types)}"
                )

            # Validate file size (max 5MB)
            content = await file.read()
            file_size = len(content)
            max_size = 5 * 1024 * 1024  # 5MB in bytes

            if file_size > max_size:
                raise ValueError(f"File too large: {file_size} bytes. Max size: {max_size} bytes (5MB)")

            # Generate unique filename
            file_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            storage_path = f"products/{unique_filename}"

            # Upload to Supabase storage
            supabase = get_service_db()

            # Upload the file
            response = supabase.storage.from_("product-images").upload(
                storage_path,
                content,
                file_options={
                    "content-type": file.content_type,
                    "cache-control": "3600",
                    "upsert": "false"
                }
            )

            # Get public URL
            public_url = supabase.storage.from_("product-images").get_public_url(storage_path)

            logger.info(f"Image uploaded successfully: {storage_path}")
            return public_url

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image: {str(e)}"
            )
