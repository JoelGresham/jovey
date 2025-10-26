"""
Pydantic models for event sourcing
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class EventCreate(BaseModel):
    """Model for creating a new event"""

    event_type: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Event type in dotted notation (e.g., 'product.created', 'order.placed')"
    )
    aggregate_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Type of entity affected (e.g., 'product', 'order', 'customer')"
    )
    aggregate_id: UUID = Field(
        ...,
        description="UUID of the specific entity instance this event affects"
    )
    data: Dict[str, Any] = Field(
        ...,
        description="Event payload - the actual event data"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context (IP address, user agent, etc.)"
    )
    created_by: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Format: 'user:{uuid}', 'agent:{name}', or 'system'"
    )
    correlation_id: Optional[UUID] = Field(
        None,
        description="Groups related events together (e.g., all events in one order flow)"
    )
    causation_id: Optional[UUID] = Field(
        None,
        description="The event that caused this event (causal chain)"
    )
    idempotency_key: Optional[str] = Field(
        None,
        max_length=255,
        description="Unique key to prevent duplicate event processing"
    )

    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        """Validate event type follows dotted notation"""
        if '.' not in v:
            raise ValueError('event_type must follow format: aggregate.action (e.g., product.created)')
        parts = v.split('.')
        if len(parts) != 2:
            raise ValueError('event_type must have exactly one dot (aggregate.action)')
        if not all(parts):
            raise ValueError('event_type parts cannot be empty')
        return v.lower()

    @field_validator('aggregate_type')
    @classmethod
    def validate_aggregate_type(cls, v: str) -> str:
        """Normalize aggregate type to lowercase"""
        return v.lower()

    @field_validator('created_by')
    @classmethod
    def validate_created_by(cls, v: str) -> str:
        """Validate created_by format"""
        if not v.startswith(('user:', 'agent:', 'system')):
            raise ValueError('created_by must start with user:, agent:, or system')
        return v


class EventResponse(BaseModel):
    """Model for event response"""

    id: UUID
    event_number: int
    event_type: str
    aggregate_type: str
    aggregate_id: UUID
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_by: str
    user_id: Optional[UUID] = None
    created_at: datetime
    event_version: int
    is_processed: bool
    processed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    correlation_id: Optional[UUID] = None
    causation_id: Optional[UUID] = None
    idempotency_key: Optional[str] = None

    model_config = {"from_attributes": True}


class EventStreamQuery(BaseModel):
    """Query parameters for event stream"""

    event_type: Optional[str] = Field(
        None,
        description="Filter by event type (e.g., 'product.created')"
    )
    aggregate_type: Optional[str] = Field(
        None,
        description="Filter by aggregate type (e.g., 'product')"
    )
    aggregate_id: Optional[UUID] = Field(
        None,
        description="Filter by specific aggregate ID"
    )
    created_by: Optional[str] = Field(
        None,
        description="Filter by creator (user:uuid, agent:name, system)"
    )
    correlation_id: Optional[UUID] = Field(
        None,
        description="Filter by correlation ID to see related events"
    )
    is_processed: Optional[bool] = Field(
        None,
        description="Filter by processing status"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of events to return"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of events to skip"
    )


class EventProcessingUpdate(BaseModel):
    """Model for updating event processing status"""

    is_processed: bool = Field(
        ...,
        description="Processing status"
    )
    processing_error: Optional[str] = Field(
        None,
        max_length=1000,
        description="Error message if processing failed"
    )


class AggregateEventHistory(BaseModel):
    """Model for aggregate event history response"""

    event_number: int
    event_type: str
    data: Dict[str, Any]
    created_by: str
    created_at: datetime


class EventTypeInfo(BaseModel):
    """Model for event type catalog"""

    event_type: str
    aggregate_type: str
    description: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    example: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
