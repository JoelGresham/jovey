# AI Agents Module

This module contains the AI agent framework and specialized agents for business functions.

## Architecture

The Jovey system uses AI agents to automate business decisions while maintaining human oversight. Each business function (Category Management, Fulfillment, Procurement, etc.) has an associated AI agent.

### Key Principles

1. **Agents READ all data** - Full visibility into system state
2. **Agents POST events** - Never write directly to database
3. **Agents COMMUNICATE peer-to-peer** - No central orchestrator
4. **Agents REQUEST approval** - Graduated autonomy (start with human approval)

## BaseAgent Class

The `BaseAgent` class provides core capabilities for all agents:

### Capabilities

| Method | Purpose | Example |
|--------|---------|---------|
| `read_data()` | Query any database table | Read product list, order history |
| `read_events()` | Query event log | Check recent changes |
| `post_event()` | Record an action/decision | Post pricing decision event |
| `make_decision()` | Use Claude API to analyze | Analyze pricing vs market |
| `message_agent()` | Send message to another agent | Request materials from Procurement |
| `read_messages()` | Check incoming messages | See requests from other agents |

### Example Usage

```python
from app.agents.base import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            function_name="my_function",
            requires_approval=True  # All decisions need human approval initially
        )

    async def analyze_and_decide(self):
        # 1. Read data
        products = await self.read_data("products", filters={"active": True})

        # 2. Make decision with Claude
        decision = await self.make_decision(
            context={"products": products},
            prompt="Should we adjust pricing? Return JSON with recommendation."
        )

        # 3. Post event for human approval
        await self.post_event(
            event_type="decision.pricing_adjustment",
            aggregate_type="product",
            aggregate_id=product_id,
            data=decision
        )
```

## Creating a New Agent

To create a new agent:

1. **Create a new file** in this directory (e.g., `fulfillment.py`)
2. **Inherit from BaseAgent**
3. **Implement agent-specific logic**
4. **Use base methods** for data access and event posting

Example template:

```python
from .base import BaseAgent
from typing import Dict, Any

class FulfillmentAgent(BaseAgent):
    \"\"\"
    AI agent for fulfillment operations
    \"\"\"

    def __init__(self):
        super().__init__(
            function_name="fulfillment",
            agent_version="1.0",
            requires_approval=True
        )

    async def prioritize_orders(self) -> Dict[str, Any]:
        \"\"\"
        Analyze orders and recommend prioritization
        \"\"\"
        # Read unfulfilled orders
        orders = await self.read_data(
            table="orders",
            filters={"status": "pending"}
        )

        # Analyze with Claude
        decision = await self.make_decision(
            context={"orders": orders},
            prompt="Prioritize these orders. Return ranked list with rationale."
        )

        # Post decision event
        await self.post_event(
            event_type="fulfillment.prioritization_recommended",
            aggregate_type="order",
            aggregate_id=orders[0]["id"],
            data=decision
        )

        return decision
```

## Agent Communication

Agents can message each other for coordination:

```python
# Production Agent requests materials from Procurement Agent
response = await self.message_agent(
    target_agent="agent:procurement",
    message_type="material_request",
    payload={
        "components_needed": ["COMP-A", "COMP-B"],
        "quantity": 100,
        "urgency": "high"
    }
)
```

## Graduated Autonomy

Agents start with `requires_approval=True`:
- All decisions posted as events
- Staff reviews and approves via UI
- Database Manager processes approved events

As confidence builds:
- Low-risk decisions can be automated (`requires_approval=False`)
- Medium-risk still needs approval
- High-risk always needs approval

## Database Tables

The agent system uses these tables:

### `agent_messages`
Stores messages between agents for peer-to-peer communication.

### `agent_decisions`
Tracks decisions made by agents, approval status, and execution results.

### Setup SQL
Run `backend/database/agent_tables.sql` in Supabase SQL Editor to create these tables.

## Current Agents

| Agent | Status | Purpose |
|-------|--------|---------|
| BaseAgent | ✅ Complete | Foundation class |
| CategoryAgent | 🔨 In Progress | Pricing and product catalog |
| FulfillmentAgent | ⏳ Planned | Order fulfillment |
| ProcurementAgent | ⏳ Planned | Material sourcing |
| ForecastingAgent | ⏳ Planned | Demand prediction |

## Testing

To test the BaseAgent class:

```bash
cd backend
python -m app.agents.example_usage
```

This runs an example workflow demonstrating all BaseAgent capabilities.

## Next Steps

1. ✅ BaseAgent class complete
2. 🔨 Create CategoryAgent (pricing decisions)
3. ⏳ Build agent decision approval UI
4. ⏳ Implement Real-time agent communication
5. ⏳ Add more specialized agents

## Resources

- Architecture: `/docs/architecture-briefing-v0.1.md`
- Technical Design: `/docs/technical-architecture.md`
- Event Sourcing: `/backend/database/events_final.sql`
- Agent Tables: `/backend/database/agent_tables.sql`
