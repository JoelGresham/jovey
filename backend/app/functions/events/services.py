"""
Service layer for event operations
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status

from app.core.database import get_service_db
from .models import (
    EventCreate,
    EventResponse,
    EventStreamQuery,
    EventProcessingUpdate,
    AggregateEventHistory,
    EventTypeInfo
)


class EventService:
    """Service for event operations"""

    @staticmethod
    async def post_event(
        event_data: EventCreate,
        user_id: Optional[UUID] = None
    ) -> EventResponse:
        """
        Post a new event to the event store.

        This is the primary way to record state changes in the system.
        All agents and system operations should post events rather than
        directly modifying state tables.

        Args:
            event_data: Event data to post
            user_id: Optional user ID if event was triggered by a user

        Returns:
            EventResponse: The created event

        Raises:
            HTTPException: If event creation fails
        """
        try:
            supabase = get_service_db()

            # Prepare event data for insertion
            insert_data = {
                "event_type": event_data.event_type,
                "aggregate_type": event_data.aggregate_type,
                "aggregate_id": str(event_data.aggregate_id),
                "data": event_data.data,
                "metadata": event_data.metadata or {},
                "created_by": event_data.created_by,
                "user_id": str(user_id) if user_id else None,
                "correlation_id": str(event_data.correlation_id) if event_data.correlation_id else None,
                "causation_id": str(event_data.causation_id) if event_data.causation_id else None,
                "idempotency_key": event_data.idempotency_key,
            }

            # Insert event
            response = supabase.table("events").insert(insert_data).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create event"
                )

            return EventResponse(**response.data[0])

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to post event: {str(e)}"
            )

    @staticmethod
    async def get_events(query: EventStreamQuery) -> List[EventResponse]:
        """
        Query the event stream with filters.

        Args:
            query: Query parameters for filtering events

        Returns:
            List[EventResponse]: List of events matching the query

        Raises:
            HTTPException: If query fails
        """
        try:
            supabase = get_service_db()

            # Build query
            query_builder = supabase.table("events").select("*")

            # Apply filters
            if query.event_type:
                query_builder = query_builder.eq("event_type", query.event_type)

            if query.aggregate_type:
                query_builder = query_builder.eq("aggregate_type", query.aggregate_type)

            if query.aggregate_id:
                query_builder = query_builder.eq("aggregate_id", str(query.aggregate_id))

            if query.created_by:
                query_builder = query_builder.eq("created_by", query.created_by)

            if query.correlation_id:
                query_builder = query_builder.eq("correlation_id", str(query.correlation_id))

            if query.is_processed is not None:
                query_builder = query_builder.eq("is_processed", query.is_processed)

            # Order by event_number descending (newest first)
            query_builder = query_builder.order("event_number", desc=True)

            # Apply pagination
            query_builder = query_builder.limit(query.limit).offset(query.offset)

            # Execute query
            response = query_builder.execute()

            return [EventResponse(**event) for event in response.data]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to query events: {str(e)}"
            )

    @staticmethod
    async def get_event_by_id(event_id: UUID) -> EventResponse:
        """
        Get a specific event by ID.

        Args:
            event_id: Event UUID

        Returns:
            EventResponse: The event

        Raises:
            HTTPException: If event not found
        """
        try:
            supabase = get_service_db()

            response = supabase.table("events").select("*").eq("id", str(event_id)).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event {event_id} not found"
                )

            return EventResponse(**response.data[0])

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get event: {str(e)}"
            )

    @staticmethod
    async def update_event_processing(
        event_id: UUID,
        update_data: EventProcessingUpdate
    ) -> EventResponse:
        """
        Update event processing status.

        This is used by the Database Manager to mark events as processed
        after they've been translated to state table updates.

        Args:
            event_id: Event UUID
            update_data: Processing status update

        Returns:
            EventResponse: Updated event

        Raises:
            HTTPException: If update fails
        """
        try:
            supabase = get_service_db()

            # Prepare update data
            update_dict = {
                "is_processed": update_data.is_processed,
                "processed_at": datetime.utcnow().isoformat() if update_data.is_processed else None,
                "processing_error": update_data.processing_error,
            }

            response = supabase.table("events").update(update_dict).eq("id", str(event_id)).execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event {event_id} not found"
                )

            return EventResponse(**response.data[0])

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update event: {str(e)}"
            )

    @staticmethod
    async def get_aggregate_history(
        aggregate_type: str,
        aggregate_id: UUID
    ) -> List[AggregateEventHistory]:
        """
        Get complete event history for a specific aggregate (entity).

        This allows reconstructing the full history of an entity from its events.

        Args:
            aggregate_type: Type of aggregate (e.g., 'product', 'order')
            aggregate_id: UUID of the specific aggregate instance

        Returns:
            List[AggregateEventHistory]: Ordered list of events for this aggregate

        Raises:
            HTTPException: If query fails
        """
        try:
            supabase = get_service_db()

            response = (
                supabase.table("events")
                .select("event_number, event_type, data, created_by, created_at")
                .eq("aggregate_type", aggregate_type.lower())
                .eq("aggregate_id", str(aggregate_id))
                .order("event_number", desc=False)  # Oldest first for history
                .execute()
            )

            return [AggregateEventHistory(**event) for event in response.data]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get aggregate history: {str(e)}"
            )

    @staticmethod
    async def get_unprocessed_events(limit: int = 100) -> List[EventResponse]:
        """
        Get events that haven't been processed yet.

        Used by the Database Manager to find events that need to be
        translated to state table updates.

        Args:
            limit: Maximum number of events to return

        Returns:
            List[EventResponse]: Unprocessed events

        Raises:
            HTTPException: If query fails
        """
        try:
            supabase = get_service_db()

            response = (
                supabase.table("events")
                .select("*")
                .eq("is_processed", False)
                .order("event_number", desc=False)  # Process in order
                .limit(limit)
                .execute()
            )

            return [EventResponse(**event) for event in response.data]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get unprocessed events: {str(e)}"
            )

    @staticmethod
    async def get_event_types() -> List[EventTypeInfo]:
        """
        Get all registered event types from the catalog.

        Returns:
            List[EventTypeInfo]: List of event type definitions

        Raises:
            HTTPException: If query fails
        """
        try:
            supabase = get_service_db()

            response = supabase.table("event_types").select("*").execute()

            return [EventTypeInfo(**event_type) for event_type in response.data]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get event types: {str(e)}"
            )

    @staticmethod
    async def get_event_stats() -> Dict[str, Any]:
        """
        Get statistics about the event stream.

        Returns:
            Dict with event statistics

        Raises:
            HTTPException: If query fails
        """
        try:
            supabase = get_service_db()

            # Get total event count
            total_response = supabase.table("events").select("count", count="exact").execute()
            total_count = total_response.count

            # Get unprocessed count
            unprocessed_response = (
                supabase.table("events")
                .select("count", count="exact")
                .eq("is_processed", False)
                .execute()
            )
            unprocessed_count = unprocessed_response.count

            # Get event type breakdown
            # Note: This requires aggregation which Supabase doesn't support directly
            # For now, we'll get all events and count in Python
            # In production, this should use a database view or function
            events_response = supabase.table("events").select("event_type, aggregate_type").execute()

            event_type_counts: Dict[str, int] = {}
            aggregate_type_counts: Dict[str, int] = {}

            for event in events_response.data:
                event_type = event["event_type"]
                aggregate_type = event["aggregate_type"]

                event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
                aggregate_type_counts[aggregate_type] = aggregate_type_counts.get(aggregate_type, 0) + 1

            return {
                "total_events": total_count,
                "unprocessed_events": unprocessed_count,
                "processed_events": total_count - unprocessed_count,
                "event_types": event_type_counts,
                "aggregate_types": aggregate_type_counts,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get event stats: {str(e)}"
            )
