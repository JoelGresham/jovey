# Jovey - AI-Native Business Operating System

**Status:** Technical Architecture Complete - Ready for Implementation
**Last Updated:** 2025-10-25

---

## What is Jovey?

Jovey is an AI-native business operating system for a household water pump manufacturing and e-commerce company. Instead of using traditional separate systems (ERP, CRM, PLM, etc.), Jovey is built as a single integrated web application where AI agents and humans collaborate to run all business operations.

### Business Context
- **Product:** Household water pumps (tank water supply, mains pressure boosting)
- **Manufacturing:** Source components from China, assemble in-house
- **Sales Channels:** Direct-to-consumer (B2C) online + Dealer/retail (B2B) channel
- **Innovation:** AI-native from inception, built to automate while maintaining human control

---

## Core Architecture Principles

1. **Single Integrated Platform** - One web app replaces entire tech stack
2. **Function-Based Design** - Each business function has its own page + AI agent
3. **Event-Sourced Data** - Agents post events, not direct database writes
4. **Peer-to-Peer AI Network** - Agents communicate directly, no central orchestrator
5. **Graduated Autonomy** - Start with human approval, automate incrementally
6. **Hybrid Interface** - Same data serves humans (visual) and AI (JSON/API)

---

## Project Documentation

### Start Here
📄 **[project-status.md](docs/project-status.md)** - Current status, decisions needed, next steps

### Core Documents
📄 **[business-context.md](docs/business-context.md)** - Jovey business use case and requirements
📄 **[architecture-briefing-v0.1.md](docs/architecture-briefing-v0.1.md)** - Complete system architecture
📄 **[technical-architecture.md](docs/technical-architecture.md)** - Detailed technical design with chosen stack
📄 **[development-setup.md](docs/development-setup.md)** - Local development environment configuration

### Navigation
- **New to the project?** Read this README, then business-context.md, then architecture-briefing
- **Picking up development?** Start with project-status.md to see where we are
- **Making decisions?** Update project-status.md decisions log
- **Starting a new session?** Review project-status.md first

---

## Current Status

**Phase:** Ready for Implementation
**Completed:**
- ✅ Business use case defined (water pump manufacturer)
- ✅ Architecture principles documented
- ✅ Technology stack decided
- ✅ Technical architecture designed
- ✅ Development approach chosen (Phase 1 MVP - 7 functions)

**Next Steps:**
- 📋 Phase 0: Project setup (Supabase, FastAPI, React)
- 📋 Database schema implementation
- 📋 Basic authentication flow
- 📋 First function development

**See [project-status.md](docs/project-status.md) for detailed status and next steps**

---

## Key Decisions Needed

Before we can start development, we need to decide:

1. **Technology Stack** - Backend framework, frontend framework, database, AI integration
2. **Development Approach** - Start with POC (2-3 functions), MVP (7 functions), or Functional Slice?
3. **Target Market** - Which geographic market to launch in first? (affects regulatory requirements)

See "What We Need to Decide Next" section in [project-status.md](docs/project-status.md)

---

## System Architecture Overview

### Business Functions (Planned)

**Phase 1 - Core Foundation (7 functions):**
- Database Manager
- Business Overview
- Platform Manager
- Category Management (product catalog, pricing)
- Customer Management (B2C + B2B)
- Fulfillment (order processing, shipping)
- Accounts Receivable (invoicing, payments)

**Phase 2 - Manufacturing (6 functions):**
- New Product Development (NPD)
- New Product Introduction (NPI)
- Production
- Procurement
- Forecasting
- Quality

**Phase 3+ - Growth (Marketing, Finance, HR, etc.)**

See [architecture-briefing-v0.1.md](docs/architecture-briefing-v0.1.md) for complete function descriptions

---

## How This System Works

### Event-Sourced Data Model
```
1. Agent observes need for action (e.g., low inventory)
2. Agent messages other agents to coordinate
3. Agent posts EVENT: "Action taken: details..."
4. Database Manager translates event to database transaction
5. Other agents read updated data, respond accordingly
```

### Human-AI Collaboration
- **Phase 1:** All decisions require human approval
- **Phase 2:** Low-risk decisions automated, others need approval
- **Phase 3:** Most operations automated, humans focus on strategy

### Dual Interface Model
- Humans access functional pages (visual dashboards)
- AI agents access same data via JSON/API
- Both views derived from identical underlying data

---

## Technology Stack

**Decided:** ✅ Complete stack selected

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Backend** | FastAPI (Python) | Modern async API, excellent AI integration, strong typing |
| **Frontend** | React | Large ecosystem, mature patterns, extensive component libraries |
| **Database** | Supabase (PostgreSQL) | PostgreSQL perfect for event sourcing + built-in auth/real-time/storage |
| **AI Engine** | Claude API (Anthropic) | Best reasoning for complex decisions, excellent instruction-following |
| **Architecture** | FastAPI-centric | Full control of business logic, Supabase handles database/auth/real-time |

**See [technical-architecture.md](docs/technical-architecture.md) for complete technical design**

---

## Development Approach

**Decided:** ✅ Phase 1 MVP (7 Functions, 2-3 months)

**Phase 1 Functions:**
1. Database Manager - Event processing and data integrity
2. Business Overview - Executive dashboard
3. Platform Manager - System evolution management
4. Category Management - Product catalog and pricing
5. Customer Management - B2C and B2B relationships
6. Fulfillment - Order processing and shipping
7. Accounts Receivable - Invoicing and payments

**Timeline:** 12 weeks (see [technical-architecture.md](docs/technical-architecture.md) for detailed phases)

**Rationale:** Build complete operational system that can run actual business, rather than limited POC

---

## For Developers

### Getting Started (Once Development Begins)
```bash
# Clone repository (already in /home/gresh/projects/jovey)
cd /home/gresh/projects/jovey

# Install dependencies (TBD based on tech stack)
# Run development server (TBD)
# Run tests (TBD)
```

### Project Structure (Planned)
```
jovey/
├── docs/                    # Documentation
│   ├── architecture-briefing-v0.1.md
│   ├── business-context.md
│   └── project-status.md
├── src/                     # Source code (TBD)
│   ├── backend/            # Backend services
│   ├── frontend/           # Frontend application
│   ├── agents/             # AI agent implementations
│   └── shared/             # Shared utilities
├── tests/                   # Tests (TBD)
└── README.md               # This file
```

**Note:** Project structure will be finalized after tech stack selection

---

## Contributing

**Current Phase:** Pre-development planning

### Decision-Making Process
1. Review relevant documentation (especially project-status.md)
2. Discuss options and implications
3. Make decision
4. **Document decision in project-status.md "Decisions Made" section**
5. Update project-status.md "Current Status"

### Documentation Standards
- All major decisions must be documented
- Update project-status.md after each session
- Keep documentation in sync with code
- Use clear, concise language
- Include rationale for decisions

---

## Contact & Resources

**Project Repository:** `/home/gresh/projects/jovey`

**Key Resources:**
- Architecture Brief: `docs/architecture-briefing-v0.1.md`
- Business Context: `docs/business-context.md`
- Project Status: `docs/project-status.md` (check here first!)

---

## License

TBD

---

## Version History

- **v0.1** (2025-10-25) - Initial documentation and business context defined
- More versions to come as we build...

---

**Ready to continue?** Check [project-status.md](docs/project-status.md) to see what needs to be decided next!
