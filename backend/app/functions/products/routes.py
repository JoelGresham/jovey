"""
Product Routes
API endpoints for product management
"""
from fastapi import APIRouter, HTTPException, status, Query, File, UploadFile, Depends
from app.functions.products.models import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductWithCategory
)
from app.functions.products.services import ProductService
from app.functions.auth.dependencies import get_current_staff_user
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get(
    "/",
    response_model=List[ProductWithCategory],
    summary="Get all products"
)
async def get_products(
    include_inactive: bool = Query(False, description="Include inactive products"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    is_featured: Optional[bool] = Query(None, description="Filter featured products"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Get all products with optional filtering

    - **include_inactive**: Include inactive products (default: false)
    - **category_id**: Filter by category UUID
    - **search**: Search term for name/description
    - **is_featured**: Filter by featured status
    - **limit**: Maximum number of results (1-500)
    - **offset**: Pagination offset
    """
    products = await ProductService.get_all_products(
        include_inactive=include_inactive,
        category_id=category_id,
        search=search,
        is_featured=is_featured,
        limit=limit,
        offset=offset
    )
    return products


@router.get(
    "/{product_id}",
    response_model=ProductWithCategory,
    summary="Get product by ID"
)
async def get_product(product_id: str):
    """
    Get a specific product by ID

    - **product_id**: UUID of the product
    """
    product = await ProductService.get_product_by_id(product_id)
    return product


@router.get(
    "/slug/{slug}",
    response_model=ProductWithCategory,
    summary="Get product by slug"
)
async def get_product_by_slug(slug: str):
    """
    Get a specific product by slug

    - **slug**: URL-friendly product identifier (e.g., '05hp-domestic-submersible')
    """
    product = await ProductService.get_product_by_slug(slug)
    return product


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product"
)
async def create_product(product_data: ProductCreate):
    """
    Create a new product

    **Required fields:**
    - **name**: Product name
    - **slug**: URL-friendly identifier (must be unique)
    - **base_price**: Base selling price

    **Optional fields:**
    - **sku**: Stock Keeping Unit (must be unique if provided)
    - **description**: Full product description
    - **short_description**: Brief description (max 500 chars)
    - **category_id**: UUID of product category
    - **sale_price**: Discounted price
    - **cost_price**: Cost to manufacture/acquire
    - **stock_quantity**: Current inventory count
    - **low_stock_threshold**: Alert threshold for low stock
    - **is_in_stock**: Stock availability status
    - **specifications**: JSON object with technical specs
    - **features**: Array of feature strings
    - **images**: Array of image URLs
    - **meta_title**: SEO page title
    - **meta_description**: SEO meta description
    - **is_featured**: Featured product flag
    - **is_active**: Active/visible status
    - **sort_order**: Display sort order
    - **manufacturer**: Manufacturer name
    - **model_number**: Model/part number
    - **warranty_months**: Warranty period in months
    - **metadata**: Additional custom data as JSON

    **Note:** Requires staff permissions
    """
    product = await ProductService.create_product(product_data)
    return product


@router.put(
    "/{product_id}",
    response_model=Product,
    summary="Update a product"
)
async def update_product(product_id: str, product_data: ProductUpdate):
    """
    Update an existing product

    - **product_id**: UUID of the product to update
    - All fields are optional - only provide fields you want to update

    **Note:** Requires staff permissions
    """
    product = await ProductService.update_product(product_id, product_data)
    return product


@router.delete(
    "/{product_id}",
    summary="Delete a product"
)
async def delete_product(product_id: str):
    """
    Delete a product (soft delete - sets is_active to false)

    - **product_id**: UUID of the product to delete

    **Note:** Requires staff permissions
    """
    result = await ProductService.delete_product(product_id)
    return result


@router.post(
    "/upload-image",
    summary="Upload product image"
)
async def upload_product_image(
    file: UploadFile = File(...),
    current_user = Depends(get_current_staff_user)
):
    """
    Upload a product image to Supabase storage

    - **file**: Image file (JPEG, PNG, WebP)

    **Note:** Requires staff permissions
    Returns the public URL of the uploaded image
    """
    try:
        image_url = await ProductService.upload_product_image(file)
        return {
            "success": True,
            "image_url": image_url,
            "message": "Image uploaded successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )
