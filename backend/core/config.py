"""
Configuration management for the Universal Consultant Intelligence Platform.

Handles environment-based configuration with comprehensive validation,
security settings, and service integration parameters.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings with comprehensive environment configuration."""
    
    # Application Settings
    app_name: str = Field("Universal Consultant Intelligence Platform", description="Application name")
    app_version: str = Field("1.0.0", description="Application version")
    debug: bool = Field(False, description="Debug mode")
    environment: str = Field("production", description="Environment (development/staging/production)")
    
    # Database Configuration
    database_url: str = Field(..., description="PostgreSQL connection string")
    database_pool_size: int = Field(20, description="Database connection pool size")
    database_max_overflow: int = Field(10, description="Database max overflow connections")
    database_pool_timeout: int = Field(30, description="Database pool timeout in seconds")
    database_pool_recycle: int = Field(3600, description="Database pool recycle time in seconds")
    
    # Redis Configuration
    redis_url: str = Field(..., description="Redis connection string")
    redis_prefix: str = Field("consultant_platform:", description="Redis key prefix")
    redis_session_timeout: int = Field(3600, description="Redis session timeout in seconds")
    redis_cache_timeout: int = Field(1800, description="Redis cache timeout in seconds")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model_gpt4: str = Field("gpt-4", description="GPT-4 model name")
    openai_model_gpt35: str = Field("gpt-3.5-turbo", description="GPT-3.5 model name")
    openai_max_tokens: int = Field(4000, description="Max tokens per request")
    openai_temperature: float = Field(0.7, description="OpenAI temperature")
    openai_max_requests_per_minute: int = Field(60, description="Max OpenAI requests per minute")
    openai_max_tokens_per_minute: int = Field(40000, description="Max OpenAI tokens per minute")
    
    # Google Custom Search API
    google_search_api_key: Optional[str] = Field(None, description="Google Search API key")
    google_search_engine_id: Optional[str] = Field(None, description="Google Custom Search Engine ID")
    google_search_rate_limit: int = Field(10, description="Google Search rate limit")
    
    # Email Configuration
    smtp_host: str = Field("smtp.gmail.com", description="SMTP host")
    smtp_port: int = Field(587, description="SMTP port")
    smtp_username: Optional[str] = Field(None, description="SMTP username")
    smtp_password: Optional[str] = Field(None, description="SMTP password")
    smtp_use_tls: bool = Field(True, description="SMTP use TLS")
    from_email: str = Field("noreply@consultantplatform.com", description="From email address")
    from_name: str = Field("Consultant Intelligence Platform", description="From name")
    
    # Security Configuration
    secret_key: str = Field(..., description="Secret key for encryption")
    api_key_prefix: str = Field("cp_", description="API key prefix")
    cors_origins: List[str] = Field(
        ["http://localhost:3000"], 
        description="CORS allowed origins"
    )
    rate_limit_per_minute: int = Field(100, description="Rate limit per minute")
    session_cookie_secure: bool = Field(True, description="Session cookie secure flag")
    session_cookie_httponly: bool = Field(True, description="Session cookie HTTP only flag")
    
    # File Storage
    upload_dir: str = Field("/app/uploads", description="Upload directory")
    max_file_size: int = Field(10485760, description="Max file size in bytes (10MB)")
    allowed_file_types: List[str] = Field(
        ["pdf", "docx", "txt", "csv"], 
        description="Allowed file types"
    )
    
    # Monitoring and Logging
    log_level: str = Field("INFO", description="Log level")
    log_format: str = Field("json", description="Log format")
    metrics_enabled: bool = Field(True, description="Enable metrics collection")
    sentry_dsn: Optional[str] = Field(None, description="Sentry DSN")
    prometheus_port: int = Field(9090, description="Prometheus metrics port")
    
    # Web Scraping Settings
    scraping_delay: float = Field(1.0, description="Delay between scraping requests in seconds")
    scraping_timeout: int = Field(30, description="Scraping timeout in seconds")
    scraping_max_retries: int = Field(3, description="Max scraping retries")
    scraping_user_agent: str = Field(
        "ConsultantPlatform/1.0 (+https://consultantplatform.com/bot)",
        description="User agent for scraping"
    )
    respect_robots_txt: bool = Field(True, description="Respect robots.txt")
    
    # Background Tasks
    celery_broker_url: str = Field("redis://localhost:6379/1", description="Celery broker URL")
    celery_result_backend: str = Field("redis://localhost:6379/2", description="Celery result backend")
    celery_worker_concurrency: int = Field(4, description="Celery worker concurrency")
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError("cors_origins must be a string or list")
    
    @validator("allowed_file_types", pre=True)
    def assemble_allowed_file_types(cls, v: str | List[str]) -> List[str]:
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError("allowed_file_types must be a string or list")
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed_environments = ["development", "staging", "production"]
        if v not in allowed_environments:
            raise ValueError(f"environment must be one of {allowed_environments}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}")
        return v.upper()
    
    @validator("openai_temperature")
    def validate_temperature(cls, v: float) -> float:
        """Validate OpenAI temperature value."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("openai_temperature must be between 0.0 and 2.0")
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("database_url must be a PostgreSQL connection string")
        return v
    
    @validator("redis_url")
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format."""
        if not v.startswith("redis://"):
            raise ValueError("redis_url must be a Redis connection string")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()