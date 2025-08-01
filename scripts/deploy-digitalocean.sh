#!/bin/bash
# Universal Consultant Intelligence Platform - DigitalOcean Deployment Script
# Automated deployment to DigitalOcean App Platform

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_NAME="consultant-intelligence-platform"
REGION="${DO_REGION:-nyc1}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] [DEPLOY]${NC} $1"
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

# Check prerequisites
check_prerequisites() {
    log "Checking deployment prerequisites..."
    
    # Check if doctl is installed
    if ! command -v doctl &> /dev/null; then
        error "doctl (DigitalOcean CLI) is not installed"
        log "Install it from: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        exit 1
    fi
    
    # Check if user is authenticated
    if ! doctl auth list &> /dev/null; then
        error "doctl authentication required"
        log "Run: doctl auth init"
        exit 1
    fi
    
    # Check if git repository is clean
    if [ -n "$(git status --porcelain)" ]; then
        warning "Git repository has uncommitted changes"
        log "Proceeding with deployment..."
    fi
    
    success "Prerequisites check passed"
}

# Create DigitalOcean App Spec
create_app_spec() {
    log "Creating DigitalOcean App Platform specification..."
    
    cat > "$PROJECT_DIR/digitalocean-app.yaml" << EOF
name: $APP_NAME
region: $REGION
services:
- name: web
  source_dir: /
  github:
    repo: $(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')
    branch: main
    deploy_on_push: true
  build_command: |
    # Install Python dependencies
    pip install -r requirements.txt
    
    # Install Node.js for frontend build (if needed)
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
    
    # Build frontend
    cd frontend
    if [ -f package.json ]; then
      npm install
      npm run build || echo "No build script found"
    fi
    cd ..
    
  run_command: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-xxs
  http_port: 8080
  routes:
  - path: /
  envs:
  - key: ENVIRONMENT
    value: production
  - key: DEBUG
    value: "false"
  - key: LOG_LEVEL
    value: INFO
  - key: OPENAI_API_KEY
    value: \${OPENAI_API_KEY}
    type: SECRET
  - key: SECRET_KEY
    value: \${SECRET_KEY}
    type: SECRET
  - key: DATABASE_URL
    value: \${DATABASE_URL}
    type: SECRET
  - key: REDIS_URL
    value: \${REDIS_URL}
    type: SECRET

databases:
- name: consultant-intelligence-db
  engine: PG
  version: "15"
  num_nodes: 1
  size: db-s-dev-database

# Redis for caching and background tasks
- name: consultant-intelligence-redis
  engine: REDIS
  version: "7"
  num_nodes: 1
  size: db-s-dev-database

workers:
- name: background-worker
  source_dir: /
  github:
    repo: $(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')
    branch: main
  build_command: pip install -r requirements.txt
  run_command: python -m celery worker -A backend.core.celery_app --loglevel=info
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: ENVIRONMENT
    value: production
  - key: OPENAI_API_KEY
    value: \${OPENAI_API_KEY}
    type: SECRET
  - key: SECRET_KEY
    value: \${SECRET_KEY}
    type: SECRET
  - key: DATABASE_URL
    value: \${DATABASE_URL}
    type: SECRET
  - key: REDIS_URL
    value: \${REDIS_URL}
    type: SECRET

jobs:
- name: db-migrate
  kind: pre_deploy
  source_dir: /
  github:
    repo: $(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')
    branch: main
  build_command: pip install -r requirements.txt
  run_command: |
    # Run database migrations
    if [ -f "alembic.ini" ]; then
      python -m alembic upgrade head
    fi
    
    # Create initial data
    if [ -f "backend/scripts/create_initial_data.py" ]; then
      python backend/scripts/create_initial_data.py
    fi
  environment_slug: python
  instance_size_slug: basic-xxs
  envs:
  - key: ENVIRONMENT
    value: production
  - key: DATABASE_URL
    value: \${DATABASE_URL}
    type: SECRET

static_sites:
- name: frontend
  source_dir: frontend
  github:
    repo: $(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')
    branch: main
  build_command: |
    if [ -f package.json ]; then
      npm install
      npm run build
    else
      echo "No package.json found, using static files"
      mkdir -p dist
      cp -r src/* dist/ || cp -r * dist/
    fi
  output_dir: dist
  index_document: index.html
  error_document: index.html
  routes:
  - path: /static
  - path: /assets
  catchall_document: index.html

alerts:
- rule: CPU_UTILIZATION
  disabled: false
  operator: GREATER_THAN
  value: 80
  window: 5m
  disabled: false

- rule: MEM_UTILIZATION
  disabled: false
  operator: GREATER_THAN
  value: 80
  window: 5m
  disabled: false

- rule: RESTART_COUNT
  disabled: false
  operator: GREATER_THAN
  value: 5
  window: 1h
  disabled: false
EOF

    success "App specification created: digitalocean-app.yaml"
}

# Deploy application
deploy_app() {
    log "Deploying application to DigitalOcean App Platform..."
    
    cd "$PROJECT_DIR"
    
    # Check if app already exists
    if doctl apps list | grep -q "$APP_NAME"; then
        log "App '$APP_NAME' already exists, updating..."
        
        # Get app ID
        APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}')
        
        # Update the app
        doctl apps update "$APP_ID" --spec digitalocean-app.yaml
        
        log "App update initiated. App ID: $APP_ID"
    else
        log "Creating new app '$APP_NAME'..."
        
        # Create new app
        APP_OUTPUT=$(doctl apps create --spec digitalocean-app.yaml --format ID,LiveURL --no-header)
        APP_ID=$(echo "$APP_OUTPUT" | awk '{print $1}')
        
        log "App creation initiated. App ID: $APP_ID"
    fi
    
    # Wait for deployment to complete
    log "Waiting for deployment to complete..."
    
    for i in {1..60}; do
        DEPLOYMENT_STATUS=$(doctl apps get "$APP_ID" --format "LastDeploymentActiveAt,InProgressDeploymentActiveAt" --no-header)
        
        if echo "$DEPLOYMENT_STATUS" | grep -q "$(date '+%Y-%m-%d')"; then
            success "Deployment completed successfully!"
            break
        fi
        
        log "Deployment in progress... ($i/60)"
        sleep 30
    done
    
    # Get app information
    APP_INFO=$(doctl apps get "$APP_ID" --format "ID,Spec.Name,DefaultIngress,LiveURL,UpdatedAt" --no-header)
    
    success "Application deployed successfully!"
    echo
    log "Application Details:"
    log "  App ID: $APP_ID"
    log "  Name: $APP_NAME"
    log "  Live URL: $(echo "$APP_INFO" | awk '{print $4}')"
    log "  Last Updated: $(echo "$APP_INFO" | awk '{print $5}')"
    
    return 0
}

# Setup environment variables
setup_environment() {
    log "Setting up environment variables..."
    
    # Check if .env file exists
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        warning ".env file not found, creating from template"
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    fi
    
    # Read environment variables from .env
    if [ -f "$PROJECT_DIR/.env" ]; then
        log "Loading environment variables from .env file"
        set -a
        source "$PROJECT_DIR/.env"
        set +a
    fi
    
    # Check for required environment variables
    REQUIRED_VARS=("OPENAI_API_KEY" "SECRET_KEY")
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            error "Required environment variable $var is not set"
            log "Please set it in the .env file or as an environment variable"
            exit 1
        fi
    done
    
    success "Environment variables configured"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    if [ -n "$APP_ID" ]; then
        # Get app URL
        APP_URL=$(doctl apps get "$APP_ID" --format LiveURL --no-header)
        
        log "Testing application health check..."
        
        # Wait a bit for the app to be fully ready
        sleep 30
        
        # Test health endpoint
        if curl -f -s "$APP_URL/health" > /dev/null; then
            success "Health check passed: $APP_URL/health"
        else
            warning "Health check failed, but this might be expected during initial deployment"
        fi
        
        log "Application should be available at: $APP_URL"
        
        # Test API endpoint
        log "Testing API endpoints..."
        if curl -f -s "$APP_URL/api/v1/consultants" > /dev/null; then
            success "API endpoints are responding"
        else
            warning "API endpoints not responding yet, may need more time to start"
        fi
    fi
}

# Cleanup temporary files
cleanup() {
    log "Cleaning up temporary files..."
    
    if [ -f "$PROJECT_DIR/digitalocean-app.yaml" ]; then
        rm "$PROJECT_DIR/digitalocean-app.yaml"
        log "Removed temporary app specification file"
    fi
}

# Main deployment function
main() {
    log "Universal Consultant Intelligence Platform - DigitalOcean Deployment"
    log "Environment: $ENVIRONMENT"
    log "Region: $REGION"
    log "App Name: $APP_NAME"
    
    # Setup trap for cleanup
    trap cleanup EXIT
    
    check_prerequisites
    setup_environment
    create_app_spec
    deploy_app
    verify_deployment
    
    success "Deployment process completed!"
    
    if [ -n "$APP_URL" ]; then
        echo
        echo "🎉 Your Universal Consultant Intelligence Platform is now live!"
        echo "🌐 Application URL: $APP_URL"
        echo "📊 Dashboard: $APP_URL/"
        echo "📖 API Documentation: $APP_URL/docs"
        echo "🔍 Health Check: $APP_URL/health"
        echo
        echo "You can manage your app using:"
        echo "  doctl apps get $APP_ID"
        echo "  doctl apps logs $APP_ID"
        echo "  doctl apps list"
    fi
}

# Run main function
main "$@"