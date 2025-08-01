"""
Prospect database models for the Universal Consultant Intelligence Platform.

Defines companies, executives, signals, and research data
with full-text search and optimized indexing.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from sqlalchemy import Column, DateTime, Index, Text, func
from sqlmodel import Field, Relationship, SQLModel


class CompanySize(str, Enum):
    """Company size enumeration."""
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class ProspectStatus(str, Enum):
    """Prospect status enumeration."""
    NEW = "new"
    RESEARCHING = "researching"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    CONVERTED = "converted"
    ARCHIVED = "archived"


class SignalType(str, Enum):
    """Signal type enumeration."""
    FUNDING = "funding"
    HIRING = "hiring"
    EXPANSION = "expansion"
    LEADERSHIP_CHANGE = "leadership_change"
    TECHNOLOGY_ADOPTION = "technology_adoption"
    PAIN_POINT = "pain_point"
    COMPETITOR_MENTION = "competitor_mention"
    PARTNERSHIP = "partnership"
    PRODUCT_LAUNCH = "product_launch"
    FINANCIAL_PERFORMANCE = "financial_performance"


class Company(SQLModel, table=True):
    """Company information and profile data."""
    
    __tablename__ = "companies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic company information
    name: str = Field(max_length=200, description="Company name", index=True)
    domain: Optional[str] = Field(max_length=100, description="Company domain", index=True)
    description: Optional[str] = Field(sa_column=Column(Text), description="Company description")
    industry: Optional[str] = Field(max_length=100, description="Industry", index=True)
    size: Optional[CompanySize] = Field(description="Company size category")
    employee_count: Optional[int] = Field(description="Number of employees")
    founded_year: Optional[int] = Field(description="Year founded")
    
    # Location information
    headquarters_city: Optional[str] = Field(max_length=100, description="HQ city")
    headquarters_state: Optional[str] = Field(max_length=50, description="HQ state")
    headquarters_country: Optional[str] = Field(max_length=50, description="HQ country", index=True)
    
    # Financial information
    revenue: Optional[str] = Field(max_length=50, description="Revenue range")
    funding_total: Optional[float] = Field(description="Total funding raised")
    latest_funding_round: Optional[str] = Field(max_length=50, description="Latest funding round")
    latest_funding_date: Optional[datetime] = Field(description="Latest funding date")
    
    # Social and web presence
    website_url: Optional[str] = Field(max_length=500, description="Website URL")
    linkedin_url: Optional[str] = Field(max_length=500, description="LinkedIn URL")
    twitter_handle: Optional[str] = Field(max_length=100, description="Twitter handle")
    
    # Company metrics and scores
    overall_score: Optional[float] = Field(default=0.0, description="Overall prospect score")
    signal_count: int = Field(default=0, description="Number of signals detected")
    last_signal_date: Optional[datetime] = Field(description="Date of last signal")
    
    # Search optimization
    search_vector: Optional[str] = Field(
        sa_column=Column("search_vector", "tsvector"),
        description="Full-text search vector"
    )
    
    # Metadata
    is_active: bool = Field(default=True, description="Whether company is active")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    # Relationships
    executives: List["Executive"] = Relationship(
        back_populates="company",
        cascade_delete=True
    )
    prospects: List["Prospect"] = Relationship(
        back_populates="company",
        cascade_delete=True
    )
    signals: List["Signal"] = Relationship(
        back_populates="company",
        cascade_delete=True
    )
    
    __table_args__ = (
        Index("idx_company_name_domain", "name", "domain"),
        Index("idx_company_industry_size", "industry", "size"),
        Index("idx_company_location", "headquarters_country", "headquarters_city"),
        Index("idx_company_score_signals", "overall_score", "signal_count"),
        Index("idx_company_search", "search_vector", postgresql_using="gin"),
        Index("idx_company_active_updated", "is_active", "updated_at"),
    )


class Executive(SQLModel, table=True):
    """Executive and key personnel information."""
    
    __tablename__ = "executives"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    
    # Personal information
    first_name: str = Field(max_length=100, description="First name")
    last_name: str = Field(max_length=100, description="Last name")
    full_name: str = Field(max_length=200, description="Full name", index=True)
    title: str = Field(max_length=200, description="Job title")
    department: Optional[str] = Field(max_length=100, description="Department")
    seniority_level: Optional[str] = Field(max_length=50, description="Seniority level")
    
    # Contact information
    email: Optional[str] = Field(max_length=200, description="Email address", index=True)
    phone: Optional[str] = Field(max_length=50, description="Phone number")
    linkedin_url: Optional[str] = Field(max_length=500, description="LinkedIn profile URL")
    twitter_handle: Optional[str] = Field(max_length=100, description="Twitter handle")
    
    # Profile information
    bio: Optional[str] = Field(sa_column=Column(Text), description="Executive bio")
    education: Optional[List[Dict]] = Field(
        default_factory=list,
        description="Education background",
        sa_column_kwargs={"type_": "JSON"}
    )
    experience: Optional[List[Dict]] = Field(
        default_factory=list,
        description="Work experience",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Engagement tracking
    engagement_score: Optional[float] = Field(default=0.0, description="Engagement score")
    last_activity_date: Optional[datetime] = Field(description="Last activity date")
    contact_attempts: int = Field(default=0, description="Number of contact attempts")
    
    # Metadata
    is_primary_contact: bool = Field(default=False, description="Primary contact for company")
    is_active: bool = Field(default=True, description="Whether executive is active")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    # Relationships
    company: Company = Relationship(back_populates="executives")
    
    __table_args__ = (
        Index("idx_executive_company_name", "company_id", "full_name"),
        Index("idx_executive_title_department", "title", "department"),
        Index("idx_executive_email", "email"),
        Index("idx_executive_primary_active", "is_primary_contact", "is_active"),
    )


class Signal(SQLModel, table=True):
    """Business signals and intelligence data."""
    
    __tablename__ = "signals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    
    # Signal identification
    signal_type: SignalType = Field(description="Type of signal", index=True)
    title: str = Field(max_length=300, description="Signal title")
    description: str = Field(sa_column=Column(Text), description="Signal description")
    
    # Signal metadata
    confidence_score: float = Field(description="AI confidence score (0.0-1.0)")
    relevance_score: float = Field(description="Relevance score for consultant (0.0-1.0)")
    impact_score: float = Field(description="Potential business impact (0.0-1.0)")
    
    # Source information
    source_url: Optional[str] = Field(max_length=1000, description="Source URL")
    source_type: Optional[str] = Field(max_length=50, description="Source type")
    source_date: Optional[datetime] = Field(description="Date from source")
    
    # Signal data
    raw_data: Optional[Dict] = Field(
        default_factory=dict,
        description="Raw signal data",
        sa_column_kwargs={"type_": "JSON"}
    )
    extracted_entities: Optional[List[Dict]] = Field(
        default_factory=list,
        description="Extracted entities (people, companies, etc.)",
        sa_column_kwargs={"type_": "JSON"}
    )
    keywords: Optional[List[str]] = Field(
        default_factory=list,
        description="Extracted keywords",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Validation and status
    is_validated: bool = Field(default=False, description="Signal has been validated")
    is_actionable: bool = Field(default=True, description="Signal is actionable")
    validation_notes: Optional[str] = Field(description="Validation notes")
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    expires_at: Optional[datetime] = Field(description="Signal expiration date")
    
    # Relationships
    company: Company = Relationship(back_populates="signals")
    
    __table_args__ = (
        Index("idx_signal_company_type", "company_id", "signal_type"),
        Index("idx_signal_scores", "confidence_score", "relevance_score", "impact_score"),
        Index("idx_signal_source_date", "source_date"),
        Index("idx_signal_validated_actionable", "is_validated", "is_actionable"),
        Index("idx_signal_created", "created_at"),
    )


class Prospect(SQLModel, table=True):
    """Prospect tracking and relationship management."""
    
    __tablename__ = "prospects"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    consultant_id: int = Field(foreign_key="consultants.id", index=True)
    company_id: int = Field(foreign_key="companies.id", index=True)
    
    # Prospect metadata
    status: ProspectStatus = Field(default=ProspectStatus.NEW, description="Prospect status", index=True)
    priority: int = Field(default=3, description="Priority (1-5, 1=highest)")
    overall_score: float = Field(default=0.0, description="Overall prospect score")
    
    # Tracking information
    first_contact_date: Optional[datetime] = Field(description="Date of first contact")
    last_contact_date: Optional[datetime] = Field(description="Date of last contact")
    next_follow_up: Optional[datetime] = Field(description="Next follow-up date")
    
    # Research and intelligence
    research_summary: Optional[str] = Field(
        sa_column=Column(Text), 
        description="AI-generated research summary"
    )
    key_insights: Optional[List[str]] = Field(
        default_factory=list,
        description="Key insights about the prospect",
        sa_column_kwargs={"type_": "JSON"}
    )
    pain_points: Optional[List[str]] = Field(
        default_factory=list,
        description="Identified pain points",
        sa_column_kwargs={"type_": "JSON"}
    )
    opportunities: Optional[List[str]] = Field(
        default_factory=list,
        description="Identified opportunities",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Engagement tracking
    email_open_count: int = Field(default=0, description="Email open count")
    email_click_count: int = Field(default=0, description="Email click count")
    email_reply_count: int = Field(default=0, description="Email reply count")
    meeting_count: int = Field(default=0, description="Number of meetings")
    
    # Notes and tags
    notes: Optional[str] = Field(sa_column=Column(Text), description="Prospect notes")
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Prospect tags",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Metadata
    is_active: bool = Field(default=True, description="Whether prospect is active")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    
    # Relationships
    consultant: "Consultant" = Relationship(back_populates="prospects")
    company: Company = Relationship(back_populates="prospects")
    
    __table_args__ = (
        Index("idx_prospect_consultant_status", "consultant_id", "status"),
        Index("idx_prospect_company", "company_id"),
        Index("idx_prospect_score_priority", "overall_score", "priority"),
        Index("idx_prospect_follow_up", "next_follow_up"),
        Index("idx_prospect_active_updated", "is_active", "updated_at"),
    )