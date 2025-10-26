"""
Service layer for Database Manager operations
"""
from typing import List, Dict, Any
from uuid import UUID
import time
import logging

from app.functions.events.services import EventService
from .event_processor import EventProcessor
from .models import (
    EventProcessingResult,
    BatchProcessingResult,
    EventToOperationMapping,
    DatabaseManagerStats
)

logger = logging.getLogger(__name__)


class DatabaseManagerService:
    """Service for Database Manager operations"""

    @staticmethod
    async def process_pending_events(limit: int = 100) -> BatchProcessingResult:
        """
        Process all pending (unprocessed) events in the event log.

        This is the main operation of the Database Manager.

        Args:
            limit: Maximum number of events to process in one batch

        Returns:
            BatchProcessingResult with statistics
        """
        start_time = time.time()

        try:
            # Get unprocessed events
            events = await EventService.get_unprocessed_events(limit)

            if not events:
                logger.info("No unprocessed events found")
                return BatchProcessingResult(
                    total_events=0,
                    successful=0,
                    failed=0,
                    processing_time_ms=0,
                    results=[]
                )

            logger.info(f"Processing {len(events)} unprocessed events")

            # Create processor
            processor = EventProcessor()

            # Process each event
            results = []
            successful = 0
            failed = 0

            for event in events:
                result = await processor.process_event(event)
                results.append(result)

                if result.success:
                    successful += 1
                else:
                    failed += 1

            processing_time = (time.time() - start_time) * 1000

            logger.info(
                f"Batch processing complete: {successful} successful, "
                f"{failed} failed, {processing_time:.2f}ms"
            )

            return BatchProcessingResult(
                total_events=len(events),
                successful=successful,
                failed=failed,
                processing_time_ms=processing_time,
                results=results
            )

        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def process_specific_events(
        event_ids: List[UUID],
        force_reprocess: bool = False
    ) -> BatchProcessingResult:
        """
        Process specific events by ID.

        Used for manual event processing or reprocessing failed events.

        Args:
            event_ids: List of event IDs to process
            force_reprocess: If True, reprocess even if already processed

        Returns:
            BatchProcessingResult with statistics
        """
        start_time = time.time()

        try:
            logger.info(f"Processing {len(event_ids)} specific events (force={force_reprocess})")

            # Fetch events
            processor = EventProcessor()
            results = []
            successful = 0
            failed = 0

            for event_id in event_ids:
                try:
                    event = await EventService.get_event_by_id(event_id)

                    # Check if already processed
                    if event.is_processed and not force_reprocess:
                        logger.warning(f"Event {event_id} already processed, skipping")
                        continue

                    # Process event
                    result = await processor.process_event(event)
                    results.append(result)

                    if result.success:
                        successful += 1
                    else:
                        failed += 1

                except Exception as e:
                    logger.error(f"Error processing event {event_id}: {str(e)}")
                    failed += 1
                    results.append(EventProcessingResult(
                        event_id=event_id,
                        event_type="unknown",
                        success=False,
                        error=str(e),
                        operations_executed=[],
                        processing_time_ms=0
                    ))

            processing_time = (time.time() - start_time) * 1000

            return BatchProcessingResult(
                total_events=len(event_ids),
                successful=successful,
                failed=failed,
                processing_time_ms=processing_time,
                results=results
            )

        except Exception as e:
            logger.error(f"Error in specific event processing: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def get_event_mappings() -> List[EventToOperationMapping]:
        """
        Get the mapping of event types to database operations.

        This documents how each event type is processed.

        Returns:
            List of event type mappings
        """
        # This is a static mapping for documentation purposes
        # In reality, the mappings are in EventProcessor handlers
        mappings = [
            EventToOperationMapping(
                event_type="product.created",
                aggregate_type="product",
                operations=["Log product creation"],
                description="Record product creation in event log"
            ),
            EventToOperationMapping(
                event_type="product.updated",
                aggregate_type="product",
                operations=["Log product update"],
                description="Record product updates in event log"
            ),
            EventToOperationMapping(
                event_type="product.price_changed",
                aggregate_type="product",
                operations=["Log price change", "Update price history"],
                description="Record price changes for audit trail"
            ),
            EventToOperationMapping(
                event_type="product.stock_updated",
                aggregate_type="product",
                operations=["Log stock update", "Check low stock alerts"],
                description="Track inventory changes"
            ),
            EventToOperationMapping(
                event_type="order.created",
                aggregate_type="order",
                operations=["Log order creation", "Reserve inventory"],
                description="Process new order creation"
            ),
            EventToOperationMapping(
                event_type="order.payment_received",
                aggregate_type="order",
                operations=["Log payment", "Update order status"],
                description="Record payment transactions"
            ),
            EventToOperationMapping(
                event_type="order.status_changed",
                aggregate_type="order",
                operations=["Log status change", "Update order status"],
                description="Track order status transitions"
            ),
            EventToOperationMapping(
                event_type="order.fulfilled",
                aggregate_type="order",
                operations=["Log fulfillment", "Send shipping notification"],
                description="Process order fulfillment"
            ),
            EventToOperationMapping(
                event_type="customer.registered",
                aggregate_type="customer",
                operations=["Log registration", "Send welcome email"],
                description="Process new customer registration"
            ),
            EventToOperationMapping(
                event_type="dealer.application_submitted",
                aggregate_type="dealer",
                operations=["Log application", "Notify staff"],
                description="Process dealer application"
            ),
            EventToOperationMapping(
                event_type="dealer.approved",
                aggregate_type="dealer",
                operations=["Log approval", "Activate account", "Send notification"],
                description="Process dealer approval"
            ),
            EventToOperationMapping(
                event_type="agent.decision_proposed",
                aggregate_type="decision",
                operations=["Log decision", "Create approval task"],
                description="Process AI agent decision proposal"
            ),
            EventToOperationMapping(
                event_type="agent.decision_approved",
                aggregate_type="decision",
                operations=["Log approval", "Execute decision"],
                description="Execute approved AI agent decision"
            ),
        ]

        return mappings

    @staticmethod
    async def get_stats() -> DatabaseManagerStats:
        """
        Get statistics about Database Manager operations.

        Returns:
            DatabaseManagerStats with current statistics
        """
        try:
            # Get event statistics
            event_stats = await EventService.get_event_stats()

            # Calculate success rate
            total_processed = event_stats.get("processed_events", 0)
            total_events = event_stats.get("total_events", 0)
            success_rate = (total_processed / total_events * 100) if total_events > 0 else 0

            # Get last processed event
            from app.functions.events.models import EventStreamQuery
            recent_processed = await EventService.get_events(
                EventStreamQuery(is_processed=True, limit=1)
            )

            last_processed_at = recent_processed[0].processed_at if recent_processed else None

            return DatabaseManagerStats(
                total_events_processed=total_processed,
                events_pending=event_stats.get("unprocessed_events", 0),
                events_failed=0,  # Would need to query processing_error field
                success_rate=success_rate,
                average_processing_time_ms=0.0,  # Would need to track this
                last_processed_at=last_processed_at,
                event_type_breakdown=event_stats.get("event_types", {})
            )

        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}", exc_info=True)
            raise
