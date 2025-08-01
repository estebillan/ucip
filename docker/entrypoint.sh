#!/bin/bash
# Universal Consultant Intelligence Platform - Docker Entrypoint Script
# Handles initialization, database setup, and service startup

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] [ENTRYPOINT]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] [SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] [WARNING]${NC} $1"
}

# Wait for database to be ready
wait_for_db() {
    log "Waiting for database to be ready..."
    
    # Extract database connection details from DATABASE_URL
    if [ -n "$DATABASE_URL" ]; then
        # Parse DATABASE_URL (format: postgresql://user:pass@host:port/dbname)
        DB_HOST=$(echo $DATABASE_URL | sed 's/.*@\([^:]*\):.*/\1/')
        DB_PORT=$(echo $DATABASE_URL | sed 's/.*:\([0-9]*\)\/.*/\1/')
        
        log "Connecting to database at $DB_HOST:$DB_PORT"
        
        # Wait for PostgreSQL to be ready
        for i in {1..30}; do
            if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
                success "Database is ready!"
                return 0
            fi
            log "Waiting for database... attempt $i/30"
            sleep 2
        done
        
        error "Database is not available after 60 seconds"
        exit 1
    else
        warning "DATABASE_URL not set, skipping database check"
    fi
}

# Wait for Redis to be ready
wait_for_redis() {
    log "Waiting for Redis to be ready..."
    
    if [ -n "$REDIS_URL" ]; then
        # Extract Redis connection details
        REDIS_HOST=$(echo $REDIS_URL | sed 's/.*@\([^:]*\):.*/\1/')
        REDIS_PORT=$(echo $REDIS_URL | sed 's/.*:\([0-9]*\)\/.*/\1/')
        
        log "Connecting to Redis at $REDIS_HOST:$REDIS_PORT"
        
        # Wait for Redis to be ready
        for i in {1..30}; do
            if nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; then
                success "Redis is ready!"
                return 0
            fi
            log "Waiting for Redis... attempt $i/30"
            sleep 2
        done
        
        error "Redis is not available after 60 seconds"
        exit 1
    else
        warning "REDIS_URL not set, skipping Redis check"
    fi
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd /app
    
    # Check if Alembic is configured
    if [ -f "alembic.ini" ]; then
        log "Running Alembic migrations..."
        python -m alembic upgrade head
        success "Database migrations completed"
    else
        log "No Alembic configuration found, skipping migrations"
    fi
}

# Create initial data
create_initial_data() {
    log "Creating initial data..."
    
    # Run initial data script if it exists
    if [ -f "/app/backend/scripts/create_initial_data.py" ]; then
        python /app/backend/scripts/create_initial_data.py
        success "Initial data created"
    else
        log "No initial data script found, skipping"
    fi
}

# Health check function
health_check() {
    log "Running health check..."
    
    if python /app/healthcheck.py; then
        success "Health check passed"
        return 0
    else
        error "Health check failed"
        return 1
    fi
}

# Validate environment
validate_environment() {
    log "Validating environment configuration..."
    
    # Check required environment variables
    REQUIRED_VARS=("DATABASE_URL")
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Warn about missing optional variables
    OPTIONAL_VARS=("OPENAI_API_KEY" "SECRET_KEY" "REDIS_URL")
    
    for var in "${OPTIONAL_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            warning "Optional environment variable $var is not set"
        fi
    done
    
    success "Environment validation completed"
}

# Set up logging
setup_logging() {
    log "Setting up logging..."
    
    # Create log directories
    mkdir -p /app/logs
    
    # Set appropriate permissions
    chown -R $(whoami):$(whoami) /app/logs
    
    success "Logging setup completed"
}

# Main execution
main() {
    log "Starting Universal Consultant Intelligence Platform..."
    log "Environment: ${ENVIRONMENT:-production}"
    log "Debug mode: ${DEBUG:-false}"
    
    # Setup logging
    setup_logging
    
    # Validate environment
    validate_environment
    
    # Wait for dependencies
    wait_for_db
    wait_for_redis
    
    # Database setup
    run_migrations
    create_initial_data
    
    # If we're running tests, don't start the main application
    if [ "$1" = "test" ]; then
        log "Running in test mode, skipping application startup"
        exec "${@:2}"
        exit 0
    fi
    
    # Start the application based on the command
    case "$1" in
        "web"|"")
            log "Starting web server..."
            exec python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-4}
            ;;
        "worker")
            log "Starting Celery worker..."
            exec python -m celery worker -A backend.core.celery_app --loglevel=${LOG_LEVEL:-info}
            ;;
        "scheduler")
            log "Starting Celery beat scheduler..."
            exec python -m celery beat -A backend.core.celery_app --loglevel=${LOG_LEVEL:-info}
            ;;
        "migrate")
            log "Running migrations only..."
            run_migrations
            success "Migrations completed, exiting"
            exit 0
            ;;
        *)
            log "Running custom command: $@"
            exec "$@"
            ;;
    esac
}

# Trap signals and pass them to the child process
trap 'kill -TERM $PID' TERM INT
main "$@" &
PID=$!
wait $PID
trap - TERM INT
wait $PID
EXIT_STATUS=$?
log "Application exited with status $EXIT_STATUS"
exit $EXIT_STATUS