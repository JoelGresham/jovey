"""
Database Connection and Client Management
Provides Supabase client instance and database utilities
"""
from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager for Supabase"""

    def __init__(self):
        self._client: Client = None
        self._service_client: Client = None

    def get_client(self) -> Client:
        """Get Supabase client with anon key (for user operations)"""
        if not self._client:
            logger.info("Initializing Supabase client...")
            try:
                self._client = create_client(
                    supabase_url=settings.supabase_url,
                    supabase_key=settings.supabase_key
                )
            except Exception as e:
                logger.error(f"Error creating Supabase client: {e}")
                raise
        return self._client

    def get_service_client(self) -> Client:
        """Get Supabase client with service role key (for admin operations)"""
        if not self._service_client:
            logger.info("Initializing Supabase service client...")
            try:
                self._service_client = create_client(
                    supabase_url=settings.supabase_url,
                    supabase_key=settings.supabase_service_key
                )
            except Exception as e:
                logger.error(f"Error creating Supabase service client: {e}")
                raise
        return self._service_client

    async def health_check(self) -> bool:
        """Check database connection health"""
        try:
            client = self.get_client()
            # Simple query to test connection
            result = client.table("_health").select("*").execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database instance
db = Database()


def get_db() -> Client:
    """Dependency for getting database client"""
    return db.get_client()


def get_service_db() -> Client:
    """Dependency for getting service database client"""
    return db.get_service_client()
