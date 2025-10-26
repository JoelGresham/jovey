"""
Order Models
Pydantic models for order management
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class OrderItemCreate(BaseModel):
    """Order item creation model"""
    product_id: UUID
    product_name: str
    product_sku: Optional[str] = None
    product_slug: Optional[str] = None
    unit_price: Decimal = Field(..., ge=0)
    quantity: int = Field(..., gt=0)
    subtotal: Decimal = Field(..., ge=0)
    specifications: dict = Field(default_factory=dict)


class OrderCreate(BaseModel):
    """Order creation model for guest and authenticated users"""
    # Customer info
    customer_email: EmailStr
    customer_first_name: str = Field(..., min_length=1, max_length=100)
    customer_last_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: Optional[str] = None

    # Shipping address
    shipping_address_line1: str = Field(..., min_length=1, max_length=255)
    shipping_address_line2: Optional[str] = None
    shipping_city: str = Field(..., min_length=1, max_length=100)
    shipping_state: str = Field(..., min_length=1, max_length=100)
    shipping_postal_code: str = Field(..., min_length=1, max_length=20)
    shipping_country: str = Field(default="India", max_length=100)

    # Billing address (optional)
    billing_address_line1: Optional[str] = None
    billing_address_line2: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_postal_code: Optional[str] = None
    billing_country: Optional[str] = Field(default="India", max_length=100)

    # Order totals
    subtotal: Decimal = Field(..., ge=0)
    shipping_cost: Decimal = Field(default=Decimal("0"), ge=0)
    tax_amount: Decimal = Field(default=Decimal("0"), ge=0)
    total_amount: Decimal = Field(..., ge=0)

    # Customer notes
    customer_notes: Optional[str] = None

    # Order items
    items: List[OrderItemCreate]

    # Optional: create account after order
    create_account: bool = False
    account_password: Optional[str] = None


class OrderItem(BaseModel):
    """Order item model"""
    id: UUID
    order_id: UUID
    product_id: Optional[UUID]
    product_name: str
    product_sku: Optional[str]
    product_slug: Optional[str]
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    specifications: dict
    created_at: datetime

    class Config:
        from_attributes = True


class Order(BaseModel):
    """Complete order model"""
    id: UUID
    order_number: str
    user_id: Optional[UUID]
    customer_email: str
    customer_first_name: str
    customer_last_name: str
    customer_phone: Optional[str]
    shipping_address_line1: str
    shipping_address_line2: Optional[str]
    shipping_city: str
    shipping_state: str
    shipping_postal_code: str
    shipping_country: str
    billing_address_line1: Optional[str]
    billing_address_line2: Optional[str]
    billing_city: Optional[str]
    billing_state: Optional[str]
    billing_postal_code: Optional[str]
    billing_country: Optional[str]
    subtotal: Decimal
    shipping_cost: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: str
    payment_status: str
    customer_notes: Optional[str]
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderWithItems(Order):
    """Order with items"""
    items: List[OrderItem] = Field(default_factory=list)


class OrderResponse(BaseModel):
    """Order creation response"""
    order: Order
    items: List[OrderItem]
    message: str
    account_created: bool = False
