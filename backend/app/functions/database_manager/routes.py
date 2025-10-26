"""
API routes for Database Manager operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from app.functions.auth.dependencies import get_current_staff_user
from .models import (
    BatchProcessingResult,
    EventToOperationMapping,
    DatabaseManagerStats,
    ManualProcessRequest
)
from .services import DatabaseManagerService


router = APIRouter(prefix="/api/v1/database-manager", tags=["Database Manager"])


@router.post("/process", response_model=BatchProcessingResult, summary="Process pending events")
async def process_pending_events(
    limit: int = Query(100, ge=1, le=1000, description="Maximum events to process"),
    current_user = Depends(get_current_staff_user)
):
    """
    Process all pending (unprocessed) events.

    **Authentication:** Staff only

    This is the main operation of the Database Manager. It:
    1. Fetches unprocessed events from the event log
    2. Translates each event to database operations
    3. Executes the operations
    4. Marks events as processed (or failed with error)

    **Processing Flow:**
    - Events are processed in chronological order (oldest first)
    - Each event is handled by its specific handler based on event_type
    - Failed events are marked with processing_error for debugging
    - Returns detailed results for each event processed

    **Use Cases:**
    - Manual processing: Staff clicks "Process Events" button
    - Scheduled processing: Cron job calls this endpoint every minute
    - On-demand processing: After important events are posted

    **Example Response:**
    ```json
    {
      "total_events": 10,
      "successful": 9,
      "failed": 1,
      "processing_time_ms": 234.5,
      "results": [
        {
          "event_id": "uuid",
          "event_type": "product.created",
          "success": true,
          "operations_executed": ["Logged product creation: SUBM-05HP-DOM-SS-50LPM-20M"],
          "processing_time_ms": 12.3
        }
      ]
    }
    ```
    """
    return await DatabaseManagerService.process_pending_events(limit)


@router.post("/process-specific", response_model=BatchProcessingResult, summary="Process specific events")
async def process_specific_events(
    request: ManualProcessRequest,
    current_user = Depends(get_current_staff_user)
):
    """
    Process specific events by ID.

    **Authentication:** Staff only

    Used for:
    - **Manual reprocessing:** Retry failed events
    - **Force reprocessing:** Reprocess events that were already processed
    - **Selective processing:** Process only specific events

    **When to Use:**
    - An event failed to process and you want to retry it
    - You fixed a bug in an event handler and want to reprocess events
    - You want to reprocess events after a data fix

    **Example Request:**
    ```json
    {
      "event_ids": [
        "123e4567-e89b-12d3-a456-426614174000",
        "987e6543-e21b-12d3-a456-426614174111"
      ],
      "force_reprocess": false
    }
    ```
    """
    return await DatabaseManagerService.process_specific_events(
        request.event_ids,
        request.force_reprocess
    )


@router.get("/mappings", response_model=List[EventToOperationMapping], summary="Get event-to-operation mappings")
async def get_event_mappings(
    current_user = Depends(get_current_staff_user)
):
    """
    Get the mapping of event types to database operations.

    **Authentication:** Staff only

    Returns documentation of how each event type is processed by the Database Manager.
    This is useful for:
    - Understanding the system behavior
    - Debugging event processing
    - Training new staff members
    - Auditing data flow

    **Example Response:**
    ```json
    [
      {
        "event_type": "product.created",
        "aggregate_type": "product",
        "operations": ["Log product creation"],
        "description": "Record product creation in event log"
      },
      {
        "event_type": "order.placed",
        "aggregate_type": "order",
        "operations": ["Log order creation", "Reserve inventory"],
        "description": "Process new order creation"
      }
    ]
    ```
    """
    return await DatabaseManagerService.get_event_mappings()


@router.get("/stats", response_model=DatabaseManagerStats, summary="Get Database Manager statistics")
async def get_stats(
    current_user = Depends(get_current_staff_user)
):
    """
    Get statistics about Database Manager operations.

    **Authentication:** Staff only

    Returns:
    - Total events processed
    - Events pending processing
    - Events that failed processing
    - Success rate (percentage)
    - Average processing time
    - When last event was processed
    - Breakdown by event type

    **Use Cases:**
    - Monitor system health
    - Check if events are being processed
    - Identify processing bottlenecks
    - Dashboard metrics

    **Example Response:**
    ```json
    {
      "total_events_processed": 1523,
      "events_pending": 5,
      "events_failed": 3,
      "success_rate": 99.8,
      "average_processing_time_ms": 15.7,
      "last_processed_at": "2025-10-26T10:30:00Z",
      "event_type_breakdown": {
        "product.created": 234,
        "order.placed": 891,
        "customer.registered": 156
      }
    }
    ```
    """
    return await DatabaseManagerService.get_stats()
