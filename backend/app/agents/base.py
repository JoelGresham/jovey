"""
BaseAgent - Foundation class for all AI agents

This class provides the core capabilities that all agents need:
- Reading data from the database
- Posting events (agents never write directly to database)
- Making decisions using Claude API
- Communicating with other agents
- Logging and error handling

All specialized agents (CategoryAgent, FulfillmentAgent, etc.) inherit from this class.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
from uuid import UUID, uuid4
from datetime import datetime
from anthropic import Anthropic
from app.core.database import get_service_db
from app.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all AI agents in the Jovey system.

    Agents follow these principles:
    1. READ all data they need from the database
    2. POST events describing actions (never write directly)
    3. COMMUNICATE with other agents via messages
    4. REQUEST human approval for decisions (graduated autonomy)

    Example usage:
    ```python
    class MyAgent(BaseAgent):
        def __init__(self):
            super().__init__(function_name="my_function")

        async def analyze_situation(self):
            # Read data
            data = await self.read_data("products", filters={"active": True})

            # Make decision
            decision = await self.make_decision(
                context={"products": data},
                prompt="Analyze these products and recommend..."
            )

            # Post event for human approval
            await self.post_event(
                event_type="decision.recommended",
                aggregate_type="product",
                aggregate_id=product_id,
                data=decision
            )
    ```
    """

    def __init__(
        self,
        function_name: str,
        agent_version: str = "1.0",
        requires_approval: bool = True
    ):
        """
        Initialize a base agent.

        Args:
            function_name: Name of the business function this agent serves (e.g., "category", "fulfillment")
            agent_version: Version of the agent (for tracking evolution)
            requires_approval: Whether agent decisions require human approval (default: True for safety)
        """
        self.function_name = function_name
        self.agent_name = f"agent:{function_name}"
        self.agent_version = agent_version
        self.requires_approval = requires_approval

        # Initialize Supabase client
        self.supabase = get_service_db()

        # Initialize Claude API client
        self.claude_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        logger.info(f"{self.agent_name} initialized (version {agent_version}, requires_approval={requires_approval})")


    # ============================================================================
    # DATA READING METHODS
    # ============================================================================

    async def read_data(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: str = "*",
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Read data from any table in the database.

        Agents can READ all data - this is how they get context for decisions.

        Args:
            table: Table name to query
            filters: Dictionary of column: value filters (uses eq operator)
            columns: Columns to select (default "*")
            order_by: Column to order by (e.g., "created_at" or "created_at.desc")
            limit: Maximum number of rows to return

        Returns:
            List of dictionaries representing rows

        Example:
            products = await self.read_data(
                table="products",
                filters={"active": True, "category": "tank_pump"},
                order_by="created_at.desc",
                limit=10
            )
        """
        try:
            query = self.supabase.table(table).select(columns)

            # Apply filters
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            # Apply ordering
            if order_by:
                if ".desc" in order_by:
                    column = order_by.replace(".desc", "")
                    query = query.order(column, desc=True)
                else:
                    query = query.order(order_by)

            # Apply limit
            if limit:
                query = query.limit(limit)

            response = query.execute()

            logger.info(f"{self.agent_name} read {len(response.data)} rows from {table}")
            return response.data

        except Exception as e:
            logger.error(f"{self.agent_name} error reading from {table}: {str(e)}")
            raise


    async def read_events(
        self,
        event_type: Optional[str] = None,
        aggregate_type: Optional[str] = None,
        aggregate_id: Optional[UUID] = None,
        processed: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Read events from the event log.

        Useful for agents to see what has happened recently or to track
        the history of a specific entity.

        Args:
            event_type: Filter by event type (e.g., "product.created")
            aggregate_type: Filter by aggregate type (e.g., "product")
            aggregate_id: Filter by specific entity ID
            processed: Filter by processing status
            limit: Maximum events to return (default 100)

        Returns:
            List of event dictionaries

        Example:
            recent_orders = await self.read_events(
                event_type="order.placed",
                processed=True,
                limit=50
            )
        """
        try:
            query = self.supabase.table("events").select("*")

            if event_type:
                query = query.eq("event_type", event_type)
            if aggregate_type:
                query = query.eq("aggregate_type", aggregate_type)
            if aggregate_id:
                query = query.eq("aggregate_id", str(aggregate_id))
            if processed is not None:
                query = query.eq("is_processed", processed)

            query = query.order("created_at", desc=True).limit(limit)

            response = query.execute()
            logger.info(f"{self.agent_name} read {len(response.data)} events")
            return response.data

        except Exception as e:
            logger.error(f"{self.agent_name} error reading events: {str(e)}")
            raise


    # ============================================================================
    # EVENT POSTING METHODS
    # ============================================================================

    async def post_event(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: Union[UUID, str],
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[UUID] = None,
        causation_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Post an event to the event log.

        This is the PRIMARY way agents affect the system. Agents never write
        directly to database tables - they post events describing what happened,
        and the Database Manager translates those to database operations.

        Args:
            event_type: Type of event (e.g., "product.price_updated")
            aggregate_type: Type of entity this affects (e.g., "product")
            aggregate_id: ID of the specific entity
            data: Event payload (the details of what happened)
            metadata: Optional additional context
            correlation_id: Optional ID linking related events
            causation_id: Optional ID of the event that caused this one

        Returns:
            The created event record

        Example:
            event = await self.post_event(
                event_type="price.adjusted",
                aggregate_type="product",
                aggregate_id=product_id,
                data={
                    "product_sku": "SUBM-05HP-DOM-SS-50LPM-20M",
                    "old_price": 1500.00,
                    "new_price": 1450.00,
                    "reason": "Market competition increased",
                    "requires_approval": True
                }
            )
        """
        try:
            # Build metadata
            full_metadata = metadata or {}
            full_metadata.update({
                "agent_name": self.agent_name,
                "agent_version": self.agent_version,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Create event
            event_data = {
                "event_type": event_type,
                "aggregate_type": aggregate_type,
                "aggregate_id": str(aggregate_id),
                "data": data,
                "metadata": full_metadata,
                "created_by": self.agent_name,
                "event_version": 1
            }

            if correlation_id:
                event_data["correlation_id"] = str(correlation_id)
            if causation_id:
                event_data["causation_id"] = str(causation_id)

            response = self.supabase.table("events").insert(event_data).execute()

            created_event = response.data[0] if response.data else None
            logger.info(f"{self.agent_name} posted event: {event_type} for {aggregate_type}:{aggregate_id}")

            return created_event

        except Exception as e:
            logger.error(f"{self.agent_name} error posting event: {str(e)}")
            raise


    # ============================================================================
    # DECISION MAKING WITH CLAUDE API
    # ============================================================================

    async def make_decision(
        self,
        context: Dict[str, Any],
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> Dict[str, Any]:
        """
        Use Claude API to analyze data and make a decision.

        This is where the AI reasoning happens. The agent provides context
        and a prompt, and Claude analyzes the situation and recommends an action.

        Args:
            context: Dictionary of data for Claude to consider
            prompt: Instructions for what Claude should analyze/decide
            system_prompt: Optional system-level instructions
            model: Claude model to use
            max_tokens: Maximum response length
            temperature: Creativity level (0-1)

        Returns:
            Dictionary with Claude's analysis and recommendation

        Example:
            decision = await self.make_decision(
                context={
                    "product": product_data,
                    "market_prices": competitor_prices,
                    "sales_history": recent_sales
                },
                prompt=\"""
                Analyze this product's pricing compared to market.
                Should we adjust the price? If so, by how much and why?
                Return JSON with: { "action": "adjust" | "maintain", "new_price": float, "rationale": "string" }
                \"""
            )
        """
        try:
            # Format context as readable text
            context_text = json.dumps(context, indent=2, default=str)

            # Build messages
            messages = [
                {
                    "role": "user",
                    "content": f"""
Context Data:
{context_text}

{prompt}

Please respond with valid JSON only.
"""
                }
            ]

            # Call Claude API
            logger.info(f"{self.agent_name} calling Claude API for decision")

            response = self.claude_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or f"You are an AI agent for the {self.function_name} function. Analyze data and make informed business decisions.",
                messages=messages
            )

            # Extract response
            response_text = response.content[0].text

            # Try to parse as JSON
            try:
                decision = json.loads(response_text)
            except json.JSONDecodeError:
                # If not valid JSON, wrap in a structure
                decision = {
                    "raw_response": response_text,
                    "parsed": False
                }

            logger.info(f"{self.agent_name} received decision from Claude")

            return decision

        except Exception as e:
            logger.error(f"{self.agent_name} error making decision with Claude: {str(e)}")
            raise


    # ============================================================================
    # AGENT COMMUNICATION METHODS
    # ============================================================================

    async def message_agent(
        self,
        target_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Send a message to another agent.

        Agents communicate peer-to-peer to coordinate decisions.

        Args:
            target_agent: Name of target agent (e.g., "agent:procurement")
            message_type: Type of message (e.g., "request", "notification")
            payload: Message data
            correlation_id: Optional ID to link request/response pairs

        Returns:
            The created message record

        Example:
            response = await self.message_agent(
                target_agent="agent:procurement",
                message_type="material_request",
                payload={
                    "component_ids": ["abc-123", "def-456"],
                    "quantity_needed": 100,
                    "urgency": "high",
                    "reason": "Production order scheduled"
                }
            )
        """
        try:
            message_data = {
                "from_agent": self.agent_name,
                "to_agent": target_agent,
                "message_type": message_type,
                "payload": payload,
                "correlation_id": str(correlation_id) if correlation_id else str(uuid4()),
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.supabase.table("agent_messages").insert(message_data).execute()

            logger.info(f"{self.agent_name} sent message to {target_agent}: {message_type}")

            return response.data[0] if response.data else None

        except Exception as e:
            logger.error(f"{self.agent_name} error sending message to {target_agent}: {str(e)}")
            raise


    async def read_messages(
        self,
        unread_only: bool = True,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Read messages sent to this agent.

        Args:
            unread_only: Only return unread messages (default True)
            limit: Maximum messages to return

        Returns:
            List of message dictionaries
        """
        try:
            query = self.supabase.table("agent_messages").select("*").eq("to_agent", self.agent_name)

            if unread_only:
                query = query.is_("read_at", "null")

            query = query.order("created_at", desc=False).limit(limit)

            response = query.execute()
            logger.info(f"{self.agent_name} read {len(response.data)} messages")

            return response.data

        except Exception as e:
            logger.error(f"{self.agent_name} error reading messages: {str(e)}")
            raise


    async def mark_message_read(self, message_id: UUID) -> bool:
        """
        Mark a message as read.

        Args:
            message_id: ID of the message

        Returns:
            True if successful
        """
        try:
            self.supabase.table("agent_messages").update({
                "read_at": datetime.utcnow().isoformat()
            }).eq("id", str(message_id)).execute()

            logger.info(f"{self.agent_name} marked message {message_id} as read")
            return True

        except Exception as e:
            logger.error(f"{self.agent_name} error marking message read: {str(e)}")
            return False


    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def log_info(self, message: str):
        """Log info message"""
        logger.info(f"{self.agent_name}: {message}")

    def log_error(self, message: str, error: Optional[Exception] = None):
        """Log error message"""
        if error:
            logger.error(f"{self.agent_name}: {message} - {str(error)}")
        else:
            logger.error(f"{self.agent_name}: {message}")

    def log_decision(self, decision_type: str, details: Dict[str, Any]):
        """Log a decision made by the agent"""
        logger.info(f"{self.agent_name} DECISION: {decision_type} - {json.dumps(details)}")
