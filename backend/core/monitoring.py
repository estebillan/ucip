"""
Monitoring and health check endpoints for the Universal Consultant Intelligence Platform.

Provides comprehensive health checks, metrics collection,
and observability for production deployment.
"""

import time
from typing import Dict, List

import structlog
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse

from backend.core.config import settings
from backend.core.database import database_health_check

logger = structlog.get_logger(__name__)


class HealthChecker:
    """Comprehensive health checking for all system components."""
    
    def __init__(self):
        self.checks: Dict[str, callable] = {
            "database": self._check_database,
            "redis": self._check_redis,
            "openai": self._check_openai,
            "storage": self._check_storage,
        }
    
    async def _check_database(self) -> Dict[str, any]:
        """Check database connectivity and performance."""
        start_time = time.time()
        
        try:
            is_healthy = await database_health_check()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "response_time": round(response_time, 3),
                "details": {
                    "connected": is_healthy,
                    "pool_size": settings.database_pool_size,
                }
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Database health check failed: {e}")
            
            return {
                "status": "unhealthy",
                "response_time": round(response_time, 3),
                "error": str(e)
            }
    
    async def _check_redis(self) -> Dict[str, any]:
        """Check Redis connectivity and performance."""
        start_time = time.time()
        
        try:
            from backend.api.dependencies import get_redis_client
            
            redis_client = await get_redis_client()
            await redis_client.ping()
            response_time = time.time() - start_time
            
            # Get Redis info
            info = await redis_client.info()
            
            return {
                "status": "healthy",
                "response_time": round(response_time, 3),
                "details": {
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory_human", "unknown"),
                    "version": info.get("redis_version", "unknown"),
                }
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Redis health check failed: {e}")
            
            return {
                "status": "unhealthy",
                "response_time": round(response_time, 3),
                "error": str(e)
            }
    
    async def _check_openai(self) -> Dict[str, any]:
        """Check OpenAI API connectivity."""
        start_time = time.time()
        
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            
            # Make a minimal API call to test connectivity
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
                temperature=0
            )
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": round(response_time, 3),
                "details": {
                    "model": response.model,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                }
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"OpenAI health check failed: {e}")
            
            return {
                "status": "unhealthy",
                "response_time": round(response_time, 3),
                "error": str(e)
            }
    
    async def _check_storage(self) -> Dict[str, any]:
        """Check storage system availability."""
        start_time = time.time()
        
        try:
            import os
            import tempfile
            
            # Test write/read to upload directory
            upload_dir = settings.upload_dir
            os.makedirs(upload_dir, exist_ok=True)
            
            # Test file operations
            test_file = os.path.join(upload_dir, "health_check.tmp")
            with open(test_file, "w") as f:
                f.write("health_check")
            
            with open(test_file, "r") as f:
                content = f.read()
            
            os.remove(test_file)
            response_time = time.time() - start_time
            
            # Get disk usage info
            disk_usage = os.statvfs(upload_dir)
            free_space = disk_usage.f_bavail * disk_usage.f_frsize
            total_space = disk_usage.f_blocks * disk_usage.f_frsize
            used_percentage = ((total_space - free_space) / total_space) * 100
            
            return {
                "status": "healthy",
                "response_time": round(response_time, 3),
                "details": {
                    "upload_dir": upload_dir,
                    "free_space_gb": round(free_space / (1024**3), 2),
                    "used_percentage": round(used_percentage, 2),
                    "writable": content == "health_check",
                }
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Storage health check failed: {e}")
            
            return {
                "status": "unhealthy",
                "response_time": round(response_time, 3),
                "error": str(e)
            }
    
    async def check_all(self) -> Dict[str, any]:
        """Run all health checks."""
        start_time = time.time()
        results = {}
        overall_status = "healthy"
        
        for check_name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[check_name] = result
                
                if result["status"] != "healthy":
                    overall_status = "degraded"
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                results[check_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                overall_status = "unhealthy"
        
        total_time = time.time() - start_time
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "response_time": round(total_time, 3),
            "version": settings.app_version,
            "environment": settings.environment,
            "checks": results
        }


# Global health checker instance
health_checker = HealthChecker()


async def health_check_endpoint():
    """Health check endpoint for load balancers and monitoring."""
    try:
        health_status = await health_checker.check_all()
        
        if health_status["status"] == "unhealthy":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health_status
            )
        elif health_status["status"] == "degraded":
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=health_status,
                headers={"X-Health-Status": "degraded"}
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=health_status
            )
    except Exception as e:
        logger.error(f"Health check endpoint failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": "Health check system failure",
                "timestamp": time.time()
            }
        )


class MetricsCollector:
    """Collect and expose application metrics."""
    
    def __init__(self):
        self.metrics = {
            "http_requests_total": 0,
            "http_request_duration_seconds": [],
            "database_queries_total": 0,
            "database_query_duration_seconds": [],
            "openai_requests_total": 0,
            "openai_tokens_used_total": 0,
            "openai_cost_total": 0.0,
            "active_connections": 0,
            "background_tasks_total": 0,
            "errors_total": 0,
        }
    
    def increment_counter(self, metric_name: str, value: int = 1):
        """Increment a counter metric."""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    def record_histogram(self, metric_name: str, value: float):
        """Record a histogram value."""
        if metric_name in self.metrics and isinstance(self.metrics[metric_name], list):
            self.metrics[metric_name].append(value)
            
            # Keep only last 1000 values to prevent memory issues
            if len(self.metrics[metric_name]) > 1000:
                self.metrics[metric_name] = self.metrics[metric_name][-1000:]
    
    def set_gauge(self, metric_name: str, value: float):
        """Set a gauge metric value."""
        if metric_name in self.metrics:
            self.metrics[metric_name] = value
    
    def get_metrics(self) -> Dict[str, any]:
        """Get current metrics snapshot."""
        processed_metrics = {}
        
        for name, value in self.metrics.items():
            if isinstance(value, list):
                # Calculate histogram statistics
                if value:
                    processed_metrics[name] = {
                        "count": len(value),
                        "sum": sum(value),
                        "avg": sum(value) / len(value),
                        "min": min(value),
                        "max": max(value),
                    }
                else:
                    processed_metrics[name] = {
                        "count": 0,
                        "sum": 0,
                        "avg": 0,
                        "min": 0,
                        "max": 0,
                    }
            else:
                processed_metrics[name] = value
        
        return processed_metrics
    
    def get_prometheus_format(self) -> str:
        """Get metrics in Prometheus format."""
        metrics = self.get_metrics()
        lines = []
        
        for name, value in metrics.items():
            if isinstance(value, dict):
                # Histogram metrics
                lines.append(f"# HELP {name} Request duration histogram")
                lines.append(f"# TYPE {name} histogram")
                lines.append(f"{name}_count {value['count']}")
                lines.append(f"{name}_sum {value['sum']}")
                lines.append(f"{name}_avg {value['avg']}")
            else:
                # Counter/gauge metrics
                metric_type = "counter" if name.endswith("_total") else "gauge"
                lines.append(f"# HELP {name} Application metric")
                lines.append(f"# TYPE {name} {metric_type}")
                lines.append(f"{name} {value}")
        
        return "\n".join(lines)


# Global metrics collector
metrics_collector = MetricsCollector()


async def metrics_endpoint():
    """Metrics endpoint for Prometheus scraping."""
    try:
        if settings.metrics_enabled:
            prometheus_metrics = metrics_collector.get_prometheus_format()
            return PlainTextResponse(
                content=prometheus_metrics,
                media_type="text/plain"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Metrics endpoint disabled"
            )
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Metrics collection error"
        )


# Middleware integration functions
def record_request_metrics(method: str, path: str, status_code: int, duration: float):
    """Record HTTP request metrics."""
    metrics_collector.increment_counter("http_requests_total")
    metrics_collector.record_histogram("http_request_duration_seconds", duration)
    
    if status_code >= 400:
        metrics_collector.increment_counter("errors_total")


def record_database_metrics(query_type: str, duration: float):
    """Record database query metrics."""
    metrics_collector.increment_counter("database_queries_total")
    metrics_collector.record_histogram("database_query_duration_seconds", duration)


def record_openai_metrics(tokens_used: int, cost: float):
    """Record OpenAI API usage metrics."""
    metrics_collector.increment_counter("openai_requests_total")
    metrics_collector.increment_counter("openai_tokens_used_total", tokens_used)
    metrics_collector.set_gauge("openai_cost_total", 
                               metrics_collector.metrics["openai_cost_total"] + cost)