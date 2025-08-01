"""
Consultant API schemas for the Universal Consultant Intelligence Platform.

Defines Pydantic models for request/response validation
with comprehensive input validation and type safety.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ConsultantBase(BaseModel):
    """Base consultant schema with core fields."""
    
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Consultant name"
    )
    consultant_type: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Type of consultant (e.g., 'fractional_cmo', 'sales_consultant')"
    )
    industry_focus: List[str] = Field(
        default_factory=list,
        description="Industries the consultant focuses on"
    )
    target_company_size: str = Field(
        ...,
        description="Target company size (startup, small, medium, large)"
    )
    geographic_preference: List[str] = Field(
        default_factory=list,
        description="Preferred geographic regions"
    )
    solution_positioning: str = Field(
        ...,
        min_length=10,
        description="How the consultant positions their solutions"
    )
    signal_priorities: Dict[str, float] = Field(
        default_factory=dict,
        description="Weighted priorities for different signals (0.0-1.0)"
    )
    is_active: bool = Field(
        default=True,
        description="Whether consultant profile is active"
    )


class ConsultantCreate(ConsultantBase):
    """Schema for creating a new consultant."""
    
    @field_validator('name', 'solution_positioning')
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        """Validate that string fields are not empty after stripping."""
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @field_validator('consultant_type')
    @classmethod
    def validate_consultant_type(cls, v: str) -> str:
        """Validate consultant type format."""
        allowed_types = {
            'fractional_cmo', 'fractional_cfo', 'fractional_coo', 'fractional_cto',
            'sales_consultant', 'marketing_consultant', 'strategy_consultant',
            'operations_consultant', 'hr_consultant', 'it_consultant',
            'finance_consultant', 'legal_consultant', 'product_consultant',
            'business_coach', 'executive_coach', 'digital_transformation'
        }
        if v.lower() not in allowed_types:
            raise ValueError(f'consultant_type must be one of: {", ".join(sorted(allowed_types))}')
        return v.lower()
    
    @field_validator('target_company_size')
    @classmethod
    def validate_company_size(cls, v: str) -> str:
        """Validate target company size."""
        allowed_sizes = {'startup', 'small', 'medium', 'large', 'enterprise'}
        if v.lower() not in allowed_sizes:
            raise ValueError(f'target_company_size must be one of: {", ".join(sorted(allowed_sizes))}')
        return v.lower()
    
    @field_validator('signal_priorities')
    @classmethod
    def validate_signal_priorities(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate signal priorities are between 0.0 and 1.0."""
        for signal_type, priority in v.items():
            if not 0.0 <= priority <= 1.0:
                raise ValueError(f'Signal priority for {signal_type} must be between 0.0 and 1.0')
        return v
    
    @field_validator('industry_focus', 'geographic_preference')
    @classmethod
    def validate_list_fields(cls, v: List[str]) -> List[str]:
        """Validate and clean list fields."""
        return [item.strip() for item in v if item.strip()]


class ConsultantUpdate(BaseModel):
    """Schema for updating a consultant."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Consultant name"
    )
    consultant_type: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Type of consultant"
    )
    industry_focus: Optional[List[str]] = Field(
        None,
        description="Industries the consultant focuses on"
    )
    target_company_size: Optional[str] = Field(
        None,
        description="Target company size"
    )
    geographic_preference: Optional[List[str]] = Field(
        None,
        description="Preferred geographic regions"
    )
    solution_positioning: Optional[str] = Field(
        None,
        min_length=10,
        description="How the consultant positions their solutions"
    )
    signal_priorities: Optional[Dict[str, float]] = Field(
        None,
        description="Weighted priorities for different signals"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether consultant profile is active"
    )
    
    @field_validator('name', 'solution_positioning')
    @classmethod
    def validate_non_empty_strings(cls, v: Optional[str]) -> Optional[str]:
        """Validate that string fields are not empty after stripping."""
        if v is not None and not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip() if v else v
    
    @field_validator('signal_priorities')
    @classmethod
    def validate_signal_priorities(cls, v: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        """Validate signal priorities are between 0.0 and 1.0."""
        if v is not None:
            for signal_type, priority in v.items():
                if not 0.0 <= priority <= 1.0:
                    raise ValueError(f'Signal priority for {signal_type} must be between 0.0 and 1.0')
        return v


class ConsultantResponse(ConsultantBase):
    """Schema for consultant API responses."""
    
    id: int = Field(description="Consultant ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ConsultantListResponse(BaseModel):
    """Schema for paginated consultant list responses."""
    
    items: List[ConsultantResponse] = Field(description="List of consultants")
    total: int = Field(description="Total number of consultants")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class ConsultantTemplateResponse(BaseModel):
    """Schema for consultant template responses."""
    
    id: int = Field(description="Template ID")
    name: str = Field(description="Template name")
    consultant_type: str = Field(description="Consultant type")
    description: str = Field(description="Template description")
    default_industry_focus: List[str] = Field(description="Default industry focus")
    default_target_company_size: str = Field(description="Default target company size")
    default_signal_priorities: Dict[str, float] = Field(description="Default signal priorities")
    signal_patterns: Dict[str, Dict] = Field(description="Signal detection patterns")
    is_active: bool = Field(description="Whether template is active")
    version: str = Field(description="Template version")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ConsultantPreferenceResponse(BaseModel):
    """Schema for consultant preference responses."""
    
    id: int = Field(description="Preference ID")
    consultant_id: int = Field(description="Consultant ID")
    email_notifications: bool = Field(description="Enable email notifications")
    research_completion_alerts: bool = Field(description="Alert on research completion")
    weekly_digest: bool = Field(description="Send weekly digest")
    auto_research_enabled: bool = Field(description="Enable automatic research")
    research_frequency: str = Field(description="Research frequency")
    max_prospects_per_day: int = Field(description="Max prospects to research per day")
    report_format: str = Field(description="Preferred report format")
    include_charts: bool = Field(description="Include charts in reports")
    include_executive_summary: bool = Field(description="Include executive summary")
    dashboard_layout: Dict[str, any] = Field(description="Dashboard layout preferences")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ConsultantPreferenceUpdate(BaseModel):
    """Schema for updating consultant preferences."""
    
    email_notifications: Optional[bool] = Field(None, description="Enable email notifications")
    research_completion_alerts: Optional[bool] = Field(None, description="Alert on research completion")
    weekly_digest: Optional[bool] = Field(None, description="Send weekly digest")
    auto_research_enabled: Optional[bool] = Field(None, description="Enable automatic research")
    research_frequency: Optional[str] = Field(None, description="Research frequency")
    max_prospects_per_day: Optional[int] = Field(None, ge=1, le=100, description="Max prospects to research per day")
    report_format: Optional[str] = Field(None, description="Preferred report format")
    include_charts: Optional[bool] = Field(None, description="Include charts in reports")
    include_executive_summary: Optional[bool] = Field(None, description="Include executive summary")
    dashboard_layout: Optional[Dict[str, any]] = Field(None, description="Dashboard layout preferences")
    
    @field_validator('research_frequency')
    @classmethod
    def validate_research_frequency(cls, v: Optional[str]) -> Optional[str]:
        """Validate research frequency."""
        if v is not None:
            allowed_frequencies = {'hourly', 'daily', 'weekly', 'monthly'}
            if v.lower() not in allowed_frequencies:
                raise ValueError(f'research_frequency must be one of: {", ".join(sorted(allowed_frequencies))}')
            return v.lower()
        return v
    
    @field_validator('report_format')
    @classmethod
    def validate_report_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate report format."""
        if v is not None:
            allowed_formats = {'pdf', 'html', 'docx', 'email'}
            if v.lower() not in allowed_formats:
                raise ValueError(f'report_format must be one of: {", ".join(sorted(allowed_formats))}')
            return v.lower()
        return v


class ConsultantStats(BaseModel):
    """Schema for consultant statistics and metrics."""
    
    total_prospects: int = Field(description="Total number of prospects")
    active_prospects: int = Field(description="Number of active prospects")
    qualified_prospects: int = Field(description="Number of qualified prospects")
    total_signals: int = Field(description="Total number of signals detected")
    recent_signals: int = Field(description="Signals detected in last 7 days")
    total_campaigns: int = Field(description="Total number of campaigns")
    active_campaigns: int = Field(description="Number of active campaigns")
    total_reports: int = Field(description="Total number of reports generated")
    recent_reports: int = Field(description="Reports generated in last 30 days")
    average_prospect_score: Optional[float] = Field(description="Average prospect score")
    conversion_rate: Optional[float] = Field(description="Conversion rate percentage")
    response_rate: Optional[float] = Field(description="Email response rate percentage")


class ConsultantDashboard(BaseModel):
    """Schema for consultant dashboard data."""
    
    consultant: ConsultantResponse = Field(description="Consultant profile")
    stats: ConsultantStats = Field(description="Consultant statistics")
    recent_prospects: List[Dict] = Field(description="Recent prospects")
    recent_signals: List[Dict] = Field(description="Recent signals")
    active_campaigns: List[Dict] = Field(description="Active campaigns")
    upcoming_tasks: List[Dict] = Field(description="Upcoming tasks")
    performance_metrics: Dict[str, any] = Field(description="Performance metrics")