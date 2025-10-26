"""
API routes for event sourcing operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from app.functions.auth.dependencies import get_current_user, get_current_staff_user
from .models import (
    EventCreate,
    EventResponse,
    EventStreamQuery,
    EventProcessingUpdate,
    AggregateEventHistory,
    EventTypeInfo
)
from .services import EventService


router = APIRouter(prefix="/api/v1/events", tags=["Events"])


@router.post("", response_model=EventResponse, summary="Post a new event")
async def post_event(
    event_data: EventCreate,
    current_user = Depends(get_current_user)
):
    """
    Post a new event to the event store.

    **This is the primary way to record state changes in the system.**

    All agents and system operations should post events rather than directly
    modifying state tables. The Database Manager will process these events
    and update the appropriate state tables.

    **Authentication:** Requires authenticated user (consumer, dealer, or staff)

    **Event Flow:**
    1. Agent/System posts event to this endpoint
    2. Event is stored immutably in the events table
    3. Database Manager picks up unprocessed events
    4. Database Manager translates events to state table updates
    5. Other agents can react to events

    **Example Event Types:**
    - `product.created` - New product added to catalog
    - `order.placed` - Customer placed an order
    - `price.changed` - Product price was updated
    - `agent.decision_proposed` - AI agent proposed a decision
    """
    # Extract user_id from current_user if it's a dict or object
    user_id = None
    if isinstance(current_user, dict):
        user_id = current_user.get("id")
    elif hasattr(current_user, "id"):
        user_id = current_user.id

    return await EventService.post_event(event_data, user_id)


@router.get("", response_model=List[EventResponse], summary="Query event stream")
async def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    aggregate_type: Optional[str] = Query(None, description="Filter by aggregate type"),
    aggregate_id: Optional[UUID] = Query(None, description="Filter by aggregate ID"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    correlation_id: Optional[UUID] = Query(None, description="Filter by correlation ID"),
    processed: Optional[bool] = Query(None, description="Filter by processing status"),
    limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    current_user = Depends(get_current_staff_user)
):
    """
    Query the event stream with filters.

    **Authentication:** Staff only

    Returns events in reverse chronological order (newest first).

    **Common Use Cases:**
    - View all events: No filters
    - View unprocessed events: `processed=false`
    - View events for a product: `aggregate_type=product&aggregate_id={uuid}`
    - View related events: `correlation_id={uuid}`
    - View agent decisions: `event_type=agent.decision_proposed`

    **Pagination:**
    - Use `limit` and `offset` for pagination
    - Default limit: 100 events
    - Maximum limit: 1000 events
    """
    query = EventStreamQuery(
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        created_by=created_by,
        correlation_id=correlation_id,
        processed=processed,
        limit=limit,
        offset=offset
    )

    return await EventService.get_events(query)


@router.get("/types", response_model=List[EventTypeInfo], summary="Get event type catalog")
async def get_event_types(
    current_user = Depends(get_current_staff_user)
):
    """
    Get all registered event types from the catalog.

    **Authentication:** Staff only

    Returns the complete catalog of event types with their descriptions,
    schemas, and examples. Use this to understand what events are available
    and how to structure event data.

    **Event Type Format:**
    - `aggregate.action` (e.g., `product.created`, `order.placed`)
    - Always lowercase
    - Descriptive action verbs: created, updated, deleted, changed, etc.
    """
    return await EventService.get_event_types()


@router.get("/stats", summary="Get event stream statistics")
async def get_event_stats(
    current_user = Depends(get_current_staff_user)
):
    """
    Get statistics about the event stream.

    **Authentication:** Staff only

    Returns:
    - Total event count
    - Processed vs unprocessed events
    - Breakdown by event type
    - Breakdown by aggregate type

    Useful for monitoring system health and Database Manager processing.
    """
    return await EventService.get_event_stats()


@router.get("/unprocessed", response_model=List[EventResponse], summary="Get unprocessed events")
async def get_unprocessed_events(
    limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
    current_user = Depends(get_current_staff_user)
):
    """
    Get events that haven't been processed yet.

    **Authentication:** Staff only

    Used by the Database Manager to find events that need to be translated
    to state table updates. Returns events in chronological order (oldest first)
    so they can be processed in the correct sequence.

    **Processing Flow:**
    1. Database Manager calls this endpoint
    2. For each event, translates to state table operation
    3. Executes state table operation
    4. Marks event as processed via PUT /events/{id}/processing
    """
    return await EventService.get_unprocessed_events(limit)


@router.get("/{event_id}", response_model=EventResponse, summary="Get event by ID")
async def get_event(
    event_id: UUID,
    current_user = Depends(get_current_staff_user)
):
    """
    Get a specific event by ID.

    **Authentication:** Staff only
    """
    return await EventService.get_event_by_id(event_id)


@router.put("/{event_id}/processing", response_model=EventResponse, summary="Update event processing status")
async def update_event_processing(
    event_id: UUID,
    update_data: EventProcessingUpdate,
    current_user = Depends(get_current_staff_user)
):
    """
    Update event processing status.

    **Authentication:** Staff only

    Used by the Database Manager to mark events as processed after they've been
    translated to state table updates. If processing fails, include an error
    message so it can be debugged.

    **Processing Status:**
    - `processed=true`: Event successfully translated to state tables
    - `processed=false, processing_error`: Event processing failed (will be retried)
    """
    return await EventService.update_event_processing(event_id, update_data)


@router.get("/aggregate/{aggregate_type}/{aggregate_id}/history", response_model=List[AggregateEventHistory], summary="Get aggregate event history")
async def get_aggregate_history(
    aggregate_type: str,
    aggregate_id: UUID,
    current_user = Depends(get_current_user)
):
    """
    Get complete event history for a specific aggregate (entity).

    **Authentication:** Requires authenticated user

    Returns all events for a specific entity in chronological order (oldest first).
    This allows reconstructing the full history of an entity from its events.

    **Examples:**
    - `GET /events/aggregate/product/{product_id}/history` - All events for a product
    - `GET /events/aggregate/order/{order_id}/history` - All events for an order
    - `GET /events/aggregate/customer/{customer_id}/history` - All events for a customer

    **Use Cases:**
    - Audit trail: "Who changed this product price and when?"
    - Time travel: "What did this order look like yesterday?"
    - Debugging: "What events led to this state?"
    - Event replay: Reconstruct current state from events
    """
    return await EventService.get_aggregate_history(aggregate_type, aggregate_id)
