"""
Logging configuration for the Universal Consultant Intelligence Platform.

Provides structured logging with correlation IDs, performance tracking,
and intelligent filtering for production environments.
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.typing import FilteringBoundLogger

from backend.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add correlation ID and timestamp
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_logger_name,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            
            # Format for JSON or console output
            structlog.processors.JSONRenderer() if settings.log_format == "json"
            else structlog.dev.ConsoleRenderer(colors=settings.debug),
        ],
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )
    
    # Set specific loggers to appropriate levels
    configure_third_party_loggers()


def configure_third_party_loggers() -> None:
    """Configure logging levels for third-party libraries."""
    
    # Reduce noise from third-party libraries
    loggers_to_quiet = [
        "uvicorn.access",
        "httpx",
        "httpcore",
        "asyncio",
        "multipart",
        "slowapi",
    ]
    
    for logger_name in loggers_to_quiet:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Database query logging
    if settings.debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Redis logging
    logging.getLogger("redis").setLevel(logging.WARNING)


class PerformanceLogger:
    """Logger for performance tracking and metrics."""
    
    def __init__(self):
        self.logger = structlog.get_logger("performance")
    
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time: float,
        user_id: str = None,
        **kwargs
    ) -> None:
        """Log API request performance."""
        self.logger.info(
            "API request",
            method=method,
            path=path,
            status_code=status_code,
            response_time=response_time,
            user_id=user_id,
            **kwargs
        )
    
    def log_database_query(
        self,
        query_type: str,
        table: str,
        execution_time: float,
        rows_affected: int = None,
        **kwargs
    ) -> None:
        """Log database query performance."""
        self.logger.info(
            "Database query",
            query_type=query_type,
            table=table,
            execution_time=execution_time,
            rows_affected=rows_affected,
            **kwargs
        )
    
    def log_external_api_call(
        self,
        service: str,
        endpoint: str,
        response_time: float,
        status_code: int = None,
        tokens_used: int = None,
        cost: float = None,
        **kwargs
    ) -> None:
        """Log external API call performance."""
        self.logger.info(
            "External API call",
            service=service,
            endpoint=endpoint,
            response_time=response_time,
            status_code=status_code,
            tokens_used=tokens_used,
            cost=cost,
            **kwargs
        )
    
    def log_background_task(
        self,
        task_name: str,
        task_id: str,
        execution_time: float,
        status: str,
        error: str = None,
        **kwargs
    ) -> None:
        """Log background task performance."""
        self.logger.info(
            "Background task",
            task_name=task_name,
            task_id=task_id,
            execution_time=execution_time,
            status=status,
            error=error,
            **kwargs
        )


class SecurityLogger:
    """Logger for security events and audit trails."""
    
    def __init__(self):
        self.logger = structlog.get_logger("security")
    
    def log_authentication_attempt(
        self,
        success: bool,
        user_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        reason: str = None,
        **kwargs
    ) -> None:
        """Log authentication attempts."""
        self.logger.info(
            "Authentication attempt",
            success=success,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            reason=reason,
            **kwargs
        )
    
    def log_authorization_failure(
        self,
        user_id: str,
        resource: str,
        action: str,
        ip_address: str = None,
        **kwargs
    ) -> None:
        """Log authorization failures."""
        self.logger.warning(
            "Authorization failure",
            user_id=user_id,
            resource=resource,
            action=action,
            ip_address=ip_address,
            **kwargs
        )
    
    def log_rate_limit_exceeded(
        self,
        ip_address: str,
        endpoint: str,
        limit: str,
        **kwargs
    ) -> None:
        """Log rate limit violations."""
        self.logger.warning(
            "Rate limit exceeded",
            ip_address=ip_address,
            endpoint=endpoint,
            limit=limit,
            **kwargs
        )
    
    def log_suspicious_activity(
        self,
        activity_type: str,
        user_id: str = None,
        ip_address: str = None,
        details: Dict[str, Any] = None,
        **kwargs
    ) -> None:
        """Log suspicious activities."""
        self.logger.error(
            "Suspicious activity detected",
            activity_type=activity_type,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            **kwargs
        )


class BusinessLogger:
    """Logger for business events and metrics."""
    
    def __init__(self):
        self.logger = structlog.get_logger("business")
    
    def log_consultant_created(
        self,
        consultant_id: int,
        consultant_type: str,
        user_id: str,
        **kwargs
    ) -> None:
        """Log consultant profile creation."""
        self.logger.info(
            "Consultant created",
            consultant_id=consultant_id,
            consultant_type=consultant_type,
            user_id=user_id,
            **kwargs
        )
    
    def log_research_task_started(
        self,
        task_id: str,
        task_type: str,
        consultant_id: int,
        target_company: str = None,
        **kwargs
    ) -> None:
        """Log research task initiation."""
        self.logger.info(
            "Research task started",
            task_id=task_id,
            task_type=task_type,
            consultant_id=consultant_id,
            target_company=target_company,
            **kwargs
        )
    
    def log_research_task_completed(
        self,
        task_id: str,
        task_type: str,
        consultant_id: int,
        execution_time: float,
        signals_found: int = None,
        cost: float = None,
        **kwargs
    ) -> None:
        """Log research task completion."""
        self.logger.info(
            "Research task completed",
            task_id=task_id,
            task_type=task_type,
            consultant_id=consultant_id,
            execution_time=execution_time,
            signals_found=signals_found,
            cost=cost,
            **kwargs
        )
    
    def log_report_generated(
        self,
        report_type: str,
        consultant_id: int,
        prospect_id: int = None,
        generation_time: float = None,
        **kwargs
    ) -> None:
        """Log report generation."""
        self.logger.info(
            "Report generated",
            report_type=report_type,
            consultant_id=consultant_id,
            prospect_id=prospect_id,
            generation_time=generation_time,
            **kwargs
        )
    
    def log_email_campaign_sent(
        self,
        campaign_id: int,
        consultant_id: int,
        recipients_count: int,
        **kwargs
    ) -> None:
        """Log email campaign dispatch."""
        self.logger.info(
            "Email campaign sent",
            campaign_id=campaign_id,
            consultant_id=consultant_id,
            recipients_count=recipients_count,
            **kwargs
        )


# Global logger instances
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()
business_logger = BusinessLogger()


def get_logger(name: str) -> FilteringBoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_exception(
    logger: FilteringBoundLogger,
    exception: Exception,
    context: Dict[str, Any] = None,
    **kwargs
) -> None:
    """Log exception with structured context."""
    logger.error(
        f"Exception occurred: {type(exception).__name__}",
        error_message=str(exception),
        error_type=type(exception).__name__,
        context=context or {},
        **kwargs,
        exc_info=True
    )