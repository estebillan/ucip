"""
Consultant database models for the Universal Consultant Intelligence Platform.

Defines consultant profiles, preferences, and signal configuration
with proper relationships and indexing for optimal query performance.
"""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Column, DateTime, Index, func
from sqlmodel import Field, Relationship, SQLModel


class ConsultantBase(SQLModel):
    """Base consultant model with core fields."""
    
    name: str = Field(max_length=100, description="Consultant name", index=True)
    consultant_type: str = Field(
        max_length=50, 
        description="Type of consultant (e.g., 'fractional_cmo', 'sales_consultant')",
        index=True
    )
    industry_focus: List[str] = Field(
        default_factory=list, 
        description="Industries the consultant focuses on",
        sa_column_kwargs={"type_": "JSON"}
    )
    target_company_size: str = Field(
        description="Target company size (startup, small, medium, large)",
        index=True
    )
    geographic_preference: List[str] = Field(
        default_factory=list, 
        description="Preferred geographic regions",
        sa_column_kwargs={"type_": "JSON"}
    )
    solution_positioning: str = Field(
        description="How the consultant positions their solutions"
    )
    signal_priorities: Dict[str, float] = Field(
        default_factory=dict, 
        description="Weighted priorities for different signals (0.0-1.0)",
        sa_column_kwargs={"type_": "JSON"}
    )
    is_active: bool = Field(default=True, description="Whether consultant profile is active")


class Consultant(ConsultantBase, table=True):
    """Consultant model with relationships and audit fields."""
    
    __tablename__ = "consultants"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    # Relationships
    prospects: List["Prospect"] = Relationship(
        back_populates="consultant",
        cascade_delete=True
    )
    campaigns: List["Campaign"] = Relationship(
        back_populates="consultant",
        cascade_delete=True
    )
    research_tasks: List["ResearchTask"] = Relationship(
        back_populates="consultant",
        cascade_delete=True
    )
    
    __table_args__ = (
        Index("idx_consultant_type_industry", "consultant_type", "industry_focus"),
        Index("idx_consultant_active_created", "is_active", "created_at"),
        Index("idx_consultant_target_size", "target_company_size"),
    )


class ConsultantTemplate(SQLModel, table=True):
    """Pre-built consultant templates with signal configurations."""
    
    __tablename__ = "consultant_templates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="Template name", unique=True)
    consultant_type: str = Field(max_length=50, description="Consultant type")
    description: str = Field(description="Template description")
    
    # Default configuration
    default_industry_focus: List[str] = Field(
        default_factory=list,
        sa_column_kwargs={"type_": "JSON"}
    )
    default_target_company_size: str = Field(description="Default company size target")
    default_signal_priorities: Dict[str, float] = Field(
        default_factory=dict,
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Signal pattern definitions
    signal_patterns: Dict[str, Dict] = Field(
        default_factory=dict,
        description="Signal detection patterns and configurations",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Template metadata
    is_active: bool = Field(default=True, description="Whether template is active")
    version: str = Field(default="1.0", description="Template version")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    __table_args__ = (
        Index("idx_template_type_active", "consultant_type", "is_active"),
        Index("idx_template_name", "name"),
    )


class ConsultantPreference(SQLModel, table=True):
    """User preferences and customization settings."""
    
    __tablename__ = "consultant_preferences"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    consultant_id: int = Field(foreign_key="consultants.id", index=True)
    
    # Notification preferences
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    research_completion_alerts: bool = Field(default=True, description="Alert on research completion")
    weekly_digest: bool = Field(default=True, description="Send weekly digest")
    
    # Research preferences
    auto_research_enabled: bool = Field(default=True, description="Enable automatic research")
    research_frequency: str = Field(default="daily", description="Research frequency")
    max_prospects_per_day: int = Field(default=10, description="Max prospects to research per day")
    
    # Report preferences
    report_format: str = Field(default="pdf", description="Preferred report format")
    include_charts: bool = Field(default=True, description="Include charts in reports")
    include_executive_summary: bool = Field(default=True, description="Include executive summary")
    
    # Dashboard preferences
    dashboard_layout: Dict[str, any] = Field(
        default_factory=dict,
        description="Dashboard layout preferences",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    __table_args__ = (
        Index("idx_preferences_consultant", "consultant_id"),
    )