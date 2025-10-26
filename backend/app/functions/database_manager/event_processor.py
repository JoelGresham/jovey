"""
Event Processor - Translates events to database operations

This is the core of the Database Manager. It reads events from the
event log and translates them into state table operations.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
import time
import logging
from datetime import datetime

from app.core.database import get_service_db
from app.functions.events.models import EventResponse
from .models import EventProcessingResult

logger = logging.getLogger(__name__)


class EventProcessor:
    """
    Processes events and updates state tables.

    This class contains the mapping logic from events to database operations.
    Each event type has a corresponding handler method.
    """

    def __init__(self):
        self.supabase = get_service_db()

    async def process_event(self, event: EventResponse) -> EventProcessingResult:
        """
        Process a single event and update state tables.

        Args:
            event: The event to process

        Returns:
            EventProcessingResult with success status and details
        """
        start_time = time.time()
        operations_executed = []

        try:
            # Route to appropriate handler based on event type
            handler_name = f"_handle_{event.event_type.replace('.', '_')}"
            handler = getattr(self, handler_name, None)

            if handler is None:
                # No specific handler, use generic handler
                logger.warning(f"No handler for event type: {event.event_type}")
                return EventProcessingResult(
                    event_id=event.id,
                    event_type=event.event_type,
                    success=False,
                    error=f"No handler for event type: {event.event_type}",
                    operations_executed=[],
                    processing_time_ms=(time.time() - start_time) * 1000
                )

            # Execute handler
            ops = await handler(event)
            operations_executed.extend(ops)

            # Mark event as processed
            await self._mark_event_processed(event.id)

            processing_time = (time.time() - start_time) * 1000

            return EventProcessingResult(
                event_id=event.id,
                event_type=event.event_type,
                success=True,
                operations_executed=operations_executed,
                processing_time_ms=processing_time
            )

        except Exception as e:
            logger.error(f"Error processing event {event.id}: {str(e)}", exc_info=True)

            # Mark event with error
            await self._mark_event_error(event.id, str(e))

            processing_time = (time.time() - start_time) * 1000

            return EventProcessingResult(
                event_id=event.id,
                event_type=event.event_type,
                success=False,
                error=str(e),
                operations_executed=operations_executed,
                processing_time_ms=processing_time
            )

    # ============================================================================
    # Product Event Handlers
    # ============================================================================

    async def _handle_product_created(self, event: EventResponse) -> List[str]:
        """Handle product.created event"""
        operations = []

        # Event already contains full product data
        # In a pure event-sourced system, products table would be updated here
        # For now, we'll log that this event was processed
        logger.info(f"Product created: {event.data.get('sku')}")
        operations.append(f"Logged product creation: {event.data.get('sku')}")

        # In future: Could trigger other events like:
        # - Notify inventory agent
        # - Update search index
        # - Send notifications

        return operations

    async def _handle_product_updated(self, event: EventResponse) -> List[str]:
        """Handle product.updated event"""
        operations = []

        product_id = event.aggregate_id
        changes = event.data.get('changes', {})

        logger.info(f"Product updated: {product_id} - {len(changes)} fields changed")
        operations.append(f"Logged product update: {product_id}")

        return operations

    async def _handle_product_price_changed(self, event: EventResponse) -> List[str]:
        """Handle product.price_changed event"""
        operations = []

        product_id = event.aggregate_id
        old_price = event.data.get('old_price')
        new_price = event.data.get('new_price')
        reason = event.data.get('reason', 'Not specified')

        logger.info(f"Price changed for {product_id}: {old_price} → {new_price} ({reason})")
        operations.append(f"Logged price change: {product_id}")

        # Could update price history table here
        # Could notify dealers of price change

        return operations

    async def _handle_product_stock_updated(self, event: EventResponse) -> List[str]:
        """Handle product.stock_updated event"""
        operations = []

        product_id = event.aggregate_id
        old_quantity = event.data.get('old_quantity')
        new_quantity = event.data.get('new_quantity')
        reason = event.data.get('reason', 'Not specified')

        logger.info(f"Stock updated for {product_id}: {old_quantity} → {new_quantity} ({reason})")
        operations.append(f"Logged stock update: {product_id}")

        # Could check for low stock alerts
        # Could notify procurement agent

        return operations

    async def _handle_product_deactivated(self, event: EventResponse) -> List[str]:
        """Handle product.deactivated event"""
        operations = []

        product_id = event.aggregate_id
        reason = event.data.get('reason', 'Not specified')

        logger.info(f"Product deactivated: {product_id} ({reason})")
        operations.append(f"Logged product deactivation: {product_id}")

        return operations

    # ============================================================================
    # Order Event Handlers
    # ============================================================================

    async def _handle_order_created(self, event: EventResponse) -> List[str]:
        """Handle order.created event"""
        operations = []

        order_id = event.aggregate_id
        customer_id = event.data.get('customer_id')
        total = event.data.get('total')
        items_count = len(event.data.get('items', []))

        logger.info(f"Order created: {order_id} - Customer: {customer_id}, Total: {total}, Items: {items_count}")
        operations.append(f"Logged order creation: {order_id}")

        # Could trigger:
        # - Inventory reservation
        # - Payment processing
        # - Notification to customer

        return operations

    async def _handle_order_payment_received(self, event: EventResponse) -> List[str]:
        """Handle order.payment_received event"""
        operations = []

        order_id = event.aggregate_id
        amount = event.data.get('amount')
        payment_method = event.data.get('payment_method')
        transaction_id = event.data.get('transaction_id')

        logger.info(f"Payment received for {order_id}: {amount} via {payment_method} (Txn: {transaction_id})")
        operations.append(f"Logged payment: {order_id}")

        # Could trigger:
        # - Update order status to paid
        # - Send confirmation email
        # - Notify fulfillment agent

        return operations

    async def _handle_order_status_changed(self, event: EventResponse) -> List[str]:
        """Handle order.status_changed event"""
        operations = []

        order_id = event.aggregate_id
        old_status = event.data.get('old_status')
        new_status = event.data.get('new_status')
        changed_by = event.data.get('changed_by')

        logger.info(f"Order status changed: {order_id} - {old_status} → {new_status} (by {changed_by})")
        operations.append(f"Logged status change: {order_id}")

        return operations

    async def _handle_order_fulfilled(self, event: EventResponse) -> List[str]:
        """Handle order.fulfilled event"""
        operations = []

        order_id = event.aggregate_id
        tracking_number = event.data.get('tracking_number')
        shipped_at = event.data.get('shipped_at')

        logger.info(f"Order fulfilled: {order_id} - Tracking: {tracking_number}")
        operations.append(f"Logged order fulfillment: {order_id}")

        # Could trigger:
        # - Send shipping notification
        # - Update inventory
        # - Calculate delivery ETA

        return operations

    async def _handle_order_cancelled(self, event: EventResponse) -> List[str]:
        """Handle order.cancelled event"""
        operations = []

        order_id = event.aggregate_id
        reason = event.data.get('reason')
        refund_amount = event.data.get('refund_amount')

        logger.info(f"Order cancelled: {order_id} - Reason: {reason}, Refund: {refund_amount}")
        operations.append(f"Logged order cancellation: {order_id}")

        # Could trigger:
        # - Process refund
        # - Release inventory
        # - Send cancellation email

        return operations

    # ============================================================================
    # Customer Event Handlers
    # ============================================================================

    async def _handle_customer_registered(self, event: EventResponse) -> List[str]:
        """Handle customer.registered event"""
        operations = []

        customer_id = event.aggregate_id
        email = event.data.get('email')
        name = event.data.get('name')

        logger.info(f"Customer registered: {customer_id} - {name} ({email})")
        operations.append(f"Logged customer registration: {customer_id}")

        # Could trigger:
        # - Send welcome email
        # - Create loyalty account
        # - Add to mailing list

        return operations

    async def _handle_customer_profile_updated(self, event: EventResponse) -> List[str]:
        """Handle customer.profile_updated event"""
        operations = []

        customer_id = event.aggregate_id
        changes = event.data.get('changes', {})

        logger.info(f"Customer profile updated: {customer_id} - {len(changes)} fields changed")
        operations.append(f"Logged profile update: {customer_id}")

        return operations

    # ============================================================================
    # Dealer Event Handlers
    # ============================================================================

    async def _handle_dealer_application_submitted(self, event: EventResponse) -> List[str]:
        """Handle dealer.application_submitted event"""
        operations = []

        dealer_id = event.aggregate_id
        business_name = event.data.get('business_name')
        email = event.data.get('email')

        logger.info(f"Dealer application submitted: {dealer_id} - {business_name} ({email})")
        operations.append(f"Logged dealer application: {dealer_id}")

        # Could trigger:
        # - Notify staff for review
        # - Run background checks
        # - Send acknowledgment email

        return operations

    async def _handle_dealer_approved(self, event: EventResponse) -> List[str]:
        """Handle dealer.approved event"""
        operations = []

        dealer_id = event.aggregate_id
        approved_by = event.data.get('approved_by')
        approved_at = event.data.get('approved_at')

        logger.info(f"Dealer approved: {dealer_id} by {approved_by}")
        operations.append(f"Logged dealer approval: {dealer_id}")

        # Could trigger:
        # - Send approval email
        # - Activate dealer account
        # - Assign pricing tier

        return operations

    async def _handle_dealer_pricing_updated(self, event: EventResponse) -> List[str]:
        """Handle dealer.pricing_updated event"""
        operations = []

        dealer_id = event.aggregate_id
        product_id = event.data.get('product_id')
        dealer_price = event.data.get('dealer_price')

        logger.info(f"Dealer pricing updated: {dealer_id} - Product: {product_id}, Price: {dealer_price}")
        operations.append(f"Logged pricing update: {dealer_id}")

        return operations

    # ============================================================================
    # Agent Decision Event Handlers
    # ============================================================================

    async def _handle_agent_decision_proposed(self, event: EventResponse) -> List[str]:
        """Handle agent.decision_proposed event"""
        operations = []

        decision_id = event.aggregate_id
        agent = event.data.get('agent')
        decision_type = event.data.get('decision_type')
        confidence = event.data.get('confidence')

        logger.info(f"Agent decision proposed: {agent} - {decision_type} (confidence: {confidence})")
        operations.append(f"Logged agent decision: {decision_id}")

        # Could trigger:
        # - Create approval task for staff
        # - Notify relevant staff members
        # - Add to decision queue

        return operations

    async def _handle_agent_decision_approved(self, event: EventResponse) -> List[str]:
        """Handle agent.decision_approved event"""
        operations = []

        decision_id = event.aggregate_id
        approved_by = event.data.get('approved_by')

        logger.info(f"Agent decision approved: {decision_id} by {approved_by}")
        operations.append(f"Logged decision approval: {decision_id}")

        # Could trigger:
        # - Execute the approved decision
        # - Update agent confidence scores
        # - Send confirmation

        return operations

    async def _handle_agent_decision_rejected(self, event: EventResponse) -> List[str]:
        """Handle agent.decision_rejected event"""
        operations = []

        decision_id = event.aggregate_id
        rejected_by = event.data.get('rejected_by')
        reason = event.data.get('reason')

        logger.info(f"Agent decision rejected: {decision_id} by {rejected_by} - {reason}")
        operations.append(f"Logged decision rejection: {decision_id}")

        # Could trigger:
        # - Update agent learning model
        # - Adjust confidence thresholds
        # - Log for agent improvement

        return operations

    # ============================================================================
    # Helper Methods
    # ============================================================================

    async def _mark_event_processed(self, event_id: UUID) -> None:
        """Mark an event as successfully processed"""
        try:
            self.supabase.table("events").update({
                "is_processed": True,
                "processed_at": datetime.utcnow().isoformat(),
                "processing_error": None
            }).eq("id", str(event_id)).execute()
        except Exception as e:
            logger.error(f"Failed to mark event {event_id} as processed: {e}")

    async def _mark_event_error(self, event_id: UUID, error: str) -> None:
        """Mark an event with a processing error"""
        try:
            self.supabase.table("events").update({
                "is_processed": False,
                "processing_error": error
            }).eq("id", str(event_id)).execute()
        except Exception as e:
            logger.error(f"Failed to mark event {event_id} with error: {e}")
