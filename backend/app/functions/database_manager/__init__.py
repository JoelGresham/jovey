"""
Database Manager function module

The Database Manager is responsible for processing events from the event log
and translating them into state table updates.
"""
from .routes import router

__all__ = ["router"]
