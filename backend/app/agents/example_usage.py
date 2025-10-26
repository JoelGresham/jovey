"""
Example Usage of BaseAgent Class

This demonstrates how to use the BaseAgent class to create AI agents.
"""

import asyncio
from uuid import uuid4
from .base import BaseAgent


class ExampleAgent(BaseAgent):
    """
    Example agent demonstrating BaseAgent capabilities
    """

    def __init__(self):
        super().__init__(
            function_name="example",
            agent_version="1.0",
            requires_approval=True
        )

    async def example_workflow(self):
        """
        Example workflow showing typical agent operations
        """

        # 1. READ DATA
        # Agents can read any data from the database
        print("Step 1: Reading product data...")
        products = await self.read_data(
            table="products",
            filters={"active": True},
            limit=5
        )
        print(f"Found {len(products)} active products")

        # 2. MAKE A DECISION
        # Use Claude API to analyze and decide
        print("\nStep 2: Making a decision with Claude...")
        decision = await self.make_decision(
            context={"products": products},
            prompt="""
            Analyze these products. Which product has the best price-to-performance ratio?
            Return JSON: { "product_sku": "string", "reason": "string" }
            """
        )
        print(f"Decision: {decision}")

        # 3. POST AN EVENT
        # Agents post events (not direct writes) to affect the system
        print("\nStep 3: Posting a decision event...")
        if len(products) > 0:
            product_id = products[0]["id"]
            event = await self.post_event(
                event_type="decision.example",
                aggregate_type="product",
                aggregate_id=product_id,
                data={
                    "decision": decision,
                    "requires_approval": True,
                    "action": "example_action"
                }
            )
            print(f"Event posted: {event['id']}")

        # 4. READ RECENT EVENTS
        # Check what's happening in the system
        print("\nStep 4: Reading recent events...")
        recent_events = await self.read_events(
            event_type="product.created",
            limit=3
        )
        print(f"Found {len(recent_events)} recent product creation events")

        # 5. SEND MESSAGE TO ANOTHER AGENT
        # Agents communicate peer-to-peer
        print("\nStep 5: Sending message to another agent...")
        message = await self.message_agent(
            target_agent="agent:category",
            message_type="notification",
            payload={
                "message": "Example workflow completed",
                "products_analyzed": len(products)
            }
        )
        print(f"Message sent: {message['id']}")

        # 6. READ MESSAGES
        # Check messages sent to this agent
        print("\nStep 6: Reading messages...")
        messages = await self.read_messages(unread_only=False, limit=5)
        print(f"Found {len(messages)} messages for this agent")

        print("\n✅ Example workflow complete!")


async def main():
    """
    Run the example
    """
    print("=" * 60)
    print("BaseAgent Example Usage")
    print("=" * 60)
    print()

    agent = ExampleAgent()
    await agent.example_workflow()


if __name__ == "__main__":
    # Run the example
    # python -m app.agents.example_usage
    asyncio.run(main())
