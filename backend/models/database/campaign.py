"""
Campaign database models for the Universal Consultant Intelligence Platform.

Defines email campaigns, templates, and engagement tracking
with comprehensive analytics and performance monitoring.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Index, Text, func
from sqlmodel import Field, Relationship, SQLModel


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EmailStatus(str, Enum):
    """Email status enumeration."""
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    REPLIED = "replied"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"
    FAILED = "failed"


class CampaignType(str, Enum):
    """Campaign type enumeration."""
    COLD_OUTREACH = "cold_outreach"
    FOLLOW_UP = "follow_up"
    NURTURE = "nurture"
    ANNOUNCEMENT = "announcement"
    NEWSLETTER = "newsletter"
    EVENT_INVITATION = "event_invitation"


class Campaign(SQLModel, table=True):
    """Email campaign management and tracking."""
    
    __tablename__ = "campaigns"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    consultant_id: int = Field(foreign_key="consultants.id", index=True)
    
    # Campaign identification
    name: str = Field(max_length=200, description="Campaign name", index=True)
    description: Optional[str] = Field(
        sa_column=Column(Text),
        description="Campaign description"
    )
    campaign_type: CampaignType = Field(description="Type of campaign", index=True)
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT, description="Campaign status", index=True)
    
    # Campaign configuration
    subject_line: str = Field(max_length=300, description="Email subject line")
    from_name: str = Field(max_length=100, description="Sender name")
    from_email: str = Field(max_length=200, description="Sender email")
    reply_to_email: Optional[str] = Field(max_length=200, description="Reply-to email")
    
    # Content and templates
    email_template_id: Optional[int] = Field(foreign_key="email_templates.id")
    email_content: str = Field(sa_column=Column(Text), description="Email content")
    personalization_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Personalization variables",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Scheduling
    scheduled_at: Optional[datetime] = Field(description="Scheduled send time")
    send_immediately: bool = Field(default=False, description="Send immediately")
    time_zone: str = Field(default="UTC", description="Time zone for scheduling")
    
    # Targeting and recipients
    target_audience: Dict[str, Any] = Field(
        default_factory=dict,
        description="Target audience criteria",
        sa_column_kwargs={"type_": "JSON"}
    )
    total_recipients: int = Field(default=0, description="Total number of recipients")
    
    # Performance tracking
    emails_sent: int = Field(default=0, description="Number of emails sent")
    emails_delivered: int = Field(default=0, description="Number of emails delivered")
    emails_opened: int = Field(default=0, description="Number of emails opened")
    emails_clicked: int = Field(default=0, description="Number of emails clicked")
    emails_replied: int = Field(default=0, description="Number of emails replied")
    emails_bounced: int = Field(default=0, description="Number of emails bounced")
    unsubscribes: int = Field(default=0, description="Number of unsubscribes")
    
    # Calculated metrics
    open_rate: Optional[float] = Field(description="Open rate percentage")
    click_rate: Optional[float] = Field(description="Click rate percentage")
    reply_rate: Optional[float] = Field(description="Reply rate percentage")
    bounce_rate: Optional[float] = Field(description="Bounce rate percentage")
    unsubscribe_rate: Optional[float] = Field(description="Unsubscribe rate percentage")
    
    # Campaign settings
    tracking_enabled: bool = Field(default=True, description="Enable email tracking")
    auto_follow_up: bool = Field(default=False, description="Enable auto follow-up")
    follow_up_delay_days: Optional[int] = Field(description="Follow-up delay in days")
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
    started_at: Optional[datetime] = Field(description="Campaign start time")
    completed_at: Optional[datetime] = Field(description="Campaign completion time")
    
    # Relationships
    consultant: "Consultant" = Relationship(back_populates="campaigns")
    email_template: Optional["EmailTemplate"] = Relationship(back_populates="campaigns")
    campaign_emails: List["CampaignEmail"] = Relationship(
        back_populates="campaign",
        cascade_delete=True
    )
    
    __table_args__ = (
        Index("idx_campaign_consultant_status", "consultant_id", "status"),
        Index("idx_campaign_type_created", "campaign_type", "created_at"),
        Index("idx_campaign_scheduled", "scheduled_at"),
        Index("idx_campaign_performance", "open_rate", "click_rate", "reply_rate"),
    )


class EmailTemplate(SQLModel, table=True):
    """Email templates for campaigns."""
    
    __tablename__ = "email_templates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    consultant_id: Optional[int] = Field(foreign_key="consultants.id", index=True)
    
    # Template identification
    name: str = Field(max_length=200, description="Template name", index=True)
    description: Optional[str] = Field(description="Template description")
    category: Optional[str] = Field(max_length=100, description="Template category", index=True)
    
    # Template content
    subject_line: str = Field(max_length=300, description="Default subject line")
    html_content: str = Field(sa_column=Column(Text), description="HTML email content")
    text_content: Optional[str] = Field(sa_column=Column(Text), description="Plain text content")
    
    # Template variables
    available_variables: List[str] = Field(
        default_factory=list,
        description="Available personalization variables",
        sa_column_kwargs={"type_": "JSON"}
    )
    required_variables: List[str] = Field(
        default_factory=list,
        description="Required personalization variables",
        sa_column_kwargs={"type_": "JSON"}
    )
    default_values: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default variable values",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Template settings
    is_active: bool = Field(default=True, description="Whether template is active")
    is_public: bool = Field(default=False, description="Template is publicly available")
    is_system_template: bool = Field(default=False, description="System-provided template")
    
    # Usage tracking
    usage_count: int = Field(default=0, description="Number of times used")
    last_used_at: Optional[datetime] = Field(description="Last usage timestamp")
    
    # Performance metrics
    average_open_rate: Optional[float] = Field(description="Average open rate")
    average_click_rate: Optional[float] = Field(description="Average click rate")
    average_reply_rate: Optional[float] = Field(description="Average reply rate")
    
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
    consultant: Optional["Consultant"] = Relationship()
    campaigns: List[Campaign] = Relationship(back_populates="email_template")
    
    __table_args__ = (
        Index("idx_template_consultant_category", "consultant_id", "category"),
        Index("idx_template_active_public", "is_active", "is_public"),
        Index("idx_template_performance", "average_open_rate", "average_click_rate"),
        Index("idx_template_usage", "usage_count", "last_used_at"),
    )


class CampaignEmail(SQLModel, table=True):
    """Individual email tracking within campaigns."""
    
    __tablename__ = "campaign_emails"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaigns.id", index=True)
    prospect_id: Optional[int] = Field(foreign_key="prospects.id", index=True)
    
    # Email identification
    email_address: str = Field(max_length=200, description="Recipient email", index=True)
    recipient_name: Optional[str] = Field(max_length=200, description="Recipient name")
    
    # Email content (personalized)
    personalized_subject: str = Field(max_length=300, description="Personalized subject line")
    personalized_content: str = Field(sa_column=Column(Text), description="Personalized email content")
    personalization_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Personalization data used",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Email status and tracking
    status: EmailStatus = Field(default=EmailStatus.DRAFT, description="Email status", index=True)
    message_id: Optional[str] = Field(max_length=200, description="Email service message ID")
    tracking_id: Optional[str] = Field(max_length=100, description="Tracking identifier", index=True)
    
    # Delivery tracking
    queued_at: Optional[datetime] = Field(description="Queued timestamp")
    sent_at: Optional[datetime] = Field(description="Sent timestamp")
    delivered_at: Optional[datetime] = Field(description="Delivered timestamp")
    
    # Engagement tracking
    first_opened_at: Optional[datetime] = Field(description="First open timestamp")
    last_opened_at: Optional[datetime] = Field(description="Last open timestamp")
    open_count: int = Field(default=0, description="Number of opens")
    
    first_clicked_at: Optional[datetime] = Field(description="First click timestamp")
    last_clicked_at: Optional[datetime] = Field(description="Last click timestamp")
    click_count: int = Field(default=0, description="Number of clicks")
    
    replied_at: Optional[datetime] = Field(description="Reply timestamp")
    reply_content: Optional[str] = Field(sa_column=Column(Text), description="Reply content")
    
    # Error tracking
    bounced_at: Optional[datetime] = Field(description="Bounce timestamp")
    bounce_reason: Optional[str] = Field(max_length=500, description="Bounce reason")
    bounce_type: Optional[str] = Field(max_length=50, description="Bounce type (soft/hard)")
    
    failed_at: Optional[datetime] = Field(description="Failure timestamp")
    failure_reason: Optional[str] = Field(max_length=500, description="Failure reason")
    
    unsubscribed_at: Optional[datetime] = Field(description="Unsubscribe timestamp")
    
    # Email metadata
    email_client: Optional[str] = Field(max_length=100, description="Email client used")
    device_type: Optional[str] = Field(max_length=50, description="Device type")
    location: Optional[str] = Field(max_length=200, description="Geographic location")
    ip_address: Optional[str] = Field(max_length=45, description="IP address")
    
    # Retry tracking
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    next_retry_at: Optional[datetime] = Field(description="Next retry timestamp")
    
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
    campaign: Campaign = Relationship(back_populates="campaign_emails")
    prospect: Optional["Prospect"] = Relationship()
    email_events: List["EmailEvent"] = Relationship(
        back_populates="campaign_email",
        cascade_delete=True
    )
    
    __table_args__ = (
        Index("idx_email_campaign_status", "campaign_id", "status"),
        Index("idx_email_recipient", "email_address"),
        Index("idx_email_tracking", "tracking_id"),
        Index("idx_email_prospect", "prospect_id"),
        Index("idx_email_sent_delivered", "sent_at", "delivered_at"),
        Index("idx_email_engagement", "first_opened_at", "first_clicked_at"),
    )


class EmailEvent(SQLModel, table=True):
    """Detailed email event tracking."""
    
    __tablename__ = "email_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_email_id: int = Field(foreign_key="campaign_emails.id", index=True)
    
    # Event details
    event_type: str = Field(max_length=50, description="Type of event", index=True)
    event_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Event metadata
    user_agent: Optional[str] = Field(max_length=500, description="User agent")
    ip_address: Optional[str] = Field(max_length=45, description="IP address")
    location: Optional[str] = Field(max_length=200, description="Geographic location")
    device_info: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Device information",
        sa_column_kwargs={"type_": "JSON"}
    )
    
    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    
    # Relationships
    campaign_email: CampaignEmail = Relationship(back_populates="email_events")
    
    __table_args__ = (
        Index("idx_event_email_type", "campaign_email_id", "event_type"),
        Index("idx_event_created", "created_at"),
    )