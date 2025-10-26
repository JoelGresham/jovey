"""
Jovey API - Main Application Entry Point
AI-Native Business Operating System for Water Pump Manufacturing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Import routers
from app.functions.auth.routes import router as auth_router
from app.functions.categories.routes import router as categories_router
from app.functions.products.routes import router as products_router
from app.functions.orders.routes import router as orders_router
from app.functions.dealers.routes import router as dealers_router
from app.functions.customers.routes import router as customers_router
from app.functions.events.routes import router as events_router
from app.functions.database_manager.routes import router as database_manager_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Jovey API",
    description="AI-Native Business Operating System for Manufacturing & E-commerce",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for frontend
from app.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(dealers_router)
app.include_router(customers_router)
app.include_router(events_router)
app.include_router(database_manager_router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Jovey API starting up...")
    logger.info("📍 Docs available at: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Jovey API shutting down...")


@app.get("/", tags=["System"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Jovey API",
        "version": "0.1.0",
        "status": "online",
        "description": "AI-Native Business Operating System"
    }


@app.get("/health", tags=["System"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "jovey-api",
        "version": "0.1.0"
    }


@app.get("/api/v1/status", tags=["System"])
async def api_status():
    """API status with more details"""
    return {
        "api_version": "v1",
        "service": "Jovey API",
        "status": "operational",
        "features": {
            "auth": "active",
            "database": "active",
            "events": "active",
            "database_manager": "active",
            "agents": "pending"
        }
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found", "path": str(request.url)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
