"""
Pydantic models for Database Manager operations
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class EventProcessingResult(BaseModel):
    """Result of processing a single event"""
    event_id: UUID
    event_type: str
    success: bool
    error: Optional[str] = None
    operations_executed: List[str] = []
    processing_time_ms: float


class BatchProcessingResult(BaseModel):
    """Result of processing multiple events"""
    total_events: int
    successful: int
    failed: int
    processing_time_ms: float
    results: List[EventProcessingResult]


class EventToOperationMapping(BaseModel):
    """Mapping of event type to database operations"""
    event_type: str
    aggregate_type: str
    operations: List[str]  # SQL operations or descriptions
    description: str


class DatabaseManagerStats(BaseModel):
    """Statistics about Database Manager operations"""
    total_events_processed: int
    events_pending: int
    events_failed: int
    success_rate: float
    average_processing_time_ms: float
    last_processed_at: Optional[datetime] = None
    event_type_breakdown: Dict[str, int]


class ManualProcessRequest(BaseModel):
    """Request to manually process specific events"""
    event_ids: List[UUID] = Field(
        ...,
        min_length=1,
        description="List of event IDs to process"
    )
    force_reprocess: bool = Field(
        default=False,
        description="Force reprocessing even if already processed"
    )
