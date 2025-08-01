"""
Research database models for the Universal Consultant Intelligence Platform.

Defines research tasks, results, and background job tracking
with comprehensive status management and audit trails.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Index, Text, func
from sqlmodel import Field, Relationship, SQLModel


class TaskStatus(str, Enum):
    """Research task status enumeration."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ResearchType(str, Enum):
    """Research type enumeration."""
    COMPANY_PROFILE = "company_profile"
    EXECUTIVE_RESEARCH = "executive_research"
    SIGNAL_REQUEST = "signal_detection"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    INDUSTRY_ANALYSIS = "industry_analysis"
    MARKET_RESEARCH = "market_research"
    FULL_INTELLIGENCE = "full_intelligence"


class ResearchTask(SQLModel, table=True):
    """Background research task tracking and management."""
    
    __tablename__ = "research_tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    consultant_id: int = Field(foreign_key="consultants.id", index=True)
    
    # Task identification
    task_id: str = Field(max_length=100, description="Unique task identifier", index=True)
    task_type: ResearchType = Field(description="Type of research task", index=True)
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status", index=True)
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Task priority")
    
    # Task configuration
    target_company: Optional[str] = Field(max_length=200, description="Target company name")
    target_domain: Optional[str] = Field(max_length=100, description="Target company domain")
    search_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Research parameters and filters",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Progress tracking
    progress_percentage: int = Field(default=0, description="Task progress (0-100)")
    current_step: Optional[str] = Field(max_length=200, description="Current processing step")
    steps_completed: List[str] = Field(
        default_factory=list,
        description="Completed processing steps",
        sa_column_kwargs={"type_": "JSON"}
    )
    total_steps: int = Field(default=1, description="Total number of steps")
    
    # Execution tracking
    started_at: Optional[datetime] = Field(description="Task start time")
    completed_at: Optional[datetime] = Field(description="Task completion time")
    execution_time_seconds: Optional[float] = Field(description="Total execution time")
    
    # Results and output
    result_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Task result data",
        sa_column_kwargs={"type_": "JSON"}
    )
    result_summary: Optional[str] = Field(
        sa_column=Column(Text),
        description="Human-readable result summary"
    )
    output_files: Optional[List[str]] = Field(
        default_factory=list,
        description="Generated output files",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Error handling
    error_message: Optional[str] = Field(
        sa_column=Column(Text),
        description="Error message if task failed"
    )
    error_details: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Detailed error information",
        sa_column_kwargs={"type_": "JSON"}
    )
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    # Resource usage
    api_calls_made: int = Field(default=0, description="Number of API calls made")
    tokens_used: int = Field(default=0, description="AI tokens consumed")
    estimated_cost: Optional[float] = Field(description="Estimated cost in USD")
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    # Relationships
    consultant: "Consultant" = Relationship(back_populates="research_tasks")
    research_results: List["ResearchResult"] = Relationship(
        back_populates="research_task",
        cascade_delete=True
    )
    
    __table_args__ = (
        Index("idx_task_consultant_status", "consultant_id", "status"),
        Index("idx_task_type_priority", "task_type", "priority"),
        Index("idx_task_created_status", "created_at", "status"),
        Index("idx_task_company_target", "target_company", "target_domain"),
        Index("idx_task_progress", "progress_percentage"),
    )


class ResearchResult(SQLModel, table=True):
    """Research results and findings storage."""
    
    __tablename__ = "research_results"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    research_task_id: int = Field(foreign_key="research_tasks.id", index=True)
    
    # Result identification
    result_type: str = Field(max_length=100, description="Type of result", index=True)
    title: str = Field(max_length=300, description="Result title")
    
    # Result data
    content: str = Field(sa_column=Column(Text), description="Result content")
    structured_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Structured result data",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Quality metrics
    confidence_score: Optional[float] = Field(description="AI confidence score (0.0-1.0)")
    relevance_score: Optional[float] = Field(description="Relevance score (0.0-1.0)")
    quality_score: Optional[float] = Field(description="Overall quality score (0.0-1.0)")
    
    # Source attribution
    source_urls: Optional[List[str]] = Field(
        default_factory=list,
        description="Source URLs for the result",
        sa_column_kwargs={"type_": "JSON"}
    )
    source_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Source metadata and attribution",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Validation and review
    is_validated: bool = Field(default=False, description="Result has been validated")
    validation_notes: Optional[str] = Field(description="Validation notes")
    manual_review_required: bool = Field(default=False, description="Requires manual review")
    
    # Usage tracking
    view_count: int = Field(default=0, description="Number of times viewed")
    last_viewed_at: Optional[datetime] = Field(description="Last view timestamp")
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    # Relationships
    research_task: ResearchTask = Relationship(back_populates="research_results")
    
    __table_args__ = (
        Index("idx_result_task_type", "research_task_id", "result_type"),
        Index("idx_result_scores", "confidence_score", "relevance_score", "quality_score"),
        Index("idx_result_validated", "is_validated", "manual_review_required"),
        Index("idx_result_created", "created_at"),
    )


class ResearchAuditLog(SQLModel, table=True):
    """Audit log for research activities and data changes."""
    
    __tablename__ = "research_audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Audit identification
    entity_type: str = Field(max_length=50, description="Type of entity changed", index=True)
    entity_id: int = Field(description="ID of the changed entity", index=True)
    action: str = Field(max_length=50, description="Action performed", index=True)
    
    # User and session tracking
    user_id: Optional[int] = Field(description="User who performed the action")
    session_id: Optional[str] = Field(max_length=100, description="Session identifier")
    ip_address: Optional[str] = Field(max_length=45, description="IP address")
    user_agent: Optional[str] = Field(max_length=500, description="User agent string")
    
    # Change tracking
    old_values: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Previous values",
        sa_column_kwargs={"type_": "JSON"}
    )
    new_values: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="New values",
        sa_column_kwargs={"type_": "JSON"}
    )
    changes_summary: Optional[str] = Field(description="Summary of changes made")
    
    # Context information
    context_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context data",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_action_created", "action", "created_at"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_session", "session_id"),
    )


class ResearchMetrics(SQLModel, table=True):
    """Research performance metrics and analytics."""
    
    __tablename__ = "research_metrics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Metric identification
    metric_date: datetime = Field(description="Date for the metrics", index=True)
    consultant_id: Optional[int] = Field(foreign_key="consultants.id", index=True)
    metric_type: str = Field(max_length=50, description="Type of metric", index=True)
    
    # Performance metrics
    tasks_created: int = Field(default=0, description="Tasks created")
    tasks_completed: int = Field(default=0, description="Tasks completed")
    tasks_failed: int = Field(default=0, description="Tasks failed")
    average_execution_time: Optional[float] = Field(description="Average execution time")
    
    # Quality metrics
    average_confidence_score: Optional[float] = Field(description="Average confidence score")
    average_relevance_score: Optional[float] = Field(description="Average relevance score")
    validation_success_rate: Optional[float] = Field(description="Validation success rate")
    
    # Resource usage metrics
    total_api_calls: int = Field(default=0, description="Total API calls made")
    total_tokens_used: int = Field(default=0, description="Total tokens consumed")
    total_cost: Optional[float] = Field(description="Total cost in USD")
    
    # Business impact metrics
    prospects_generated: int = Field(default=0, description="Prospects generated")
    signals_detected: int = Field(default=0, description="Signals detected")
    reports_generated: int = Field(default=0, description="Reports generated")
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    __table_args__ = (
        Index("idx_metrics_date_consultant", "metric_date", "consultant_id"),
        Index("idx_metrics_type_date", "metric_type", "metric_date"),
    )