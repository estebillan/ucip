#!/bin/bash
# Universal Consultant Intelligence Platform - Build and Deploy Script
# Comprehensive Docker build and deployment automation

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="consultant-intelligence"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] [BUILD]${NC} $1"
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

# Help function
show_help() {
    cat << EOF
Universal Consultant Intelligence Platform - Build Script

Usage: $0 [OPTIONS] [COMMAND]

Commands:
    build           Build Docker image (default)
    test            Run tests in Docker container
    dev             Start development environment
    prod            Start production environment
    deploy          Build and deploy to production
    clean           Clean up Docker resources
    push            Push image to registry
    pull            Pull image from registry

Options:
    -h, --help      Show this help message
    -t, --tag TAG   Image tag (default: latest)
    -r, --registry  Registry URL for push/pull
    -e, --env ENV   Environment (dev|prod, default: production)
    --no-cache      Build without using cache
    --parallel      Build with parallel processing
    --verbose       Verbose output

Examples:
    $0 build --tag v1.0.0
    $0 dev
    $0 deploy --registry your-registry.com
    $0 test
EOF
}

# Parse command line arguments
parse_args() {
    NO_CACHE=""
    PARALLEL=""
    VERBOSE=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -r|--registry)
                REGISTRY="$2"
                shift 2
                ;;
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --no-cache)
                NO_CACHE="--no-cache"
                shift
                ;;
            --parallel)
                PARALLEL="--parallel"
                shift
                ;;
            --verbose)
                VERBOSE="--verbose"
                shift
                ;;
            build|test|dev|prod|deploy|clean|push|pull)
                COMMAND="$1"
                shift
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    COMMAND="${COMMAND:-build}"
}

# Validate environment
validate_environment() {
    log "Validating build environment..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        warning "docker-compose not found, will use 'docker compose' instead"
    fi
    
    success "Environment validation passed"
}

# Build Docker image
build_image() {
    log "Building Docker image: $IMAGE_NAME:$IMAGE_TAG"
    
    cd "$PROJECT_DIR"
    
    # Build arguments
    BUILD_ARGS=(
        "--tag" "$IMAGE_NAME:$IMAGE_TAG"
        "--file" "Dockerfile"
        $NO_CACHE
    )
    
    if [ -n "$PARALLEL" ]; then
        BUILD_ARGS+=("--progress" "plain")
    fi
    
    if [ -n "$VERBOSE" ]; then
        BUILD_ARGS+=("--progress" "plain")
    fi
    
    log "Docker build command: docker build ${BUILD_ARGS[*]} ."
    
    if docker build "${BUILD_ARGS[@]}" .; then
        success "Docker image built successfully: $IMAGE_NAME:$IMAGE_TAG"
        
        # Tag as latest if not already
        if [ "$IMAGE_TAG" != "latest" ]; then
            docker tag "$IMAGE_NAME:$IMAGE_TAG" "$IMAGE_NAME:latest"
            log "Tagged image as latest"
        fi
    else
        error "Docker build failed"
        exit 1
    fi
}

# Run tests
run_tests() {
    log "Running tests in Docker container..."
    
    cd "$PROJECT_DIR"
    
    # Build test image
    docker build -t "$IMAGE_NAME:test" --target backend-builder .
    
    # Run Python tests
    log "Running Python unit tests..."
    docker run --rm \
        -v "$PROJECT_DIR:/app" \
        -e ENVIRONMENT=testing \
        "$IMAGE_NAME:test" \
        python -m pytest tests/ -v
    
    # Run Playwright tests (if available)
    if [ -f "playwright.config.js" ]; then
        log "Running Playwright end-to-end tests..."
        docker run --rm \
            -v "$PROJECT_DIR:/app" \
            -e ENVIRONMENT=testing \
            "$IMAGE_NAME:test" \
            sh -c "npx playwright install && npx playwright test"
    fi
    
    success "All tests passed"
}

# Start development environment
start_dev() {
    log "Starting development environment..."
    
    cd "$PROJECT_DIR"
    
    # Use development docker-compose
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
    
    success "Development environment started"
    log "Services available at:"
    log "  - Application: http://localhost:8001"
    log "  - Frontend (if enabled): http://localhost:3000"
    log "  - pgAdmin: http://localhost:5050 (admin@consultant.local / admin123)"
    log "  - Redis Commander: http://localhost:8081 (admin / admin123)"
}

# Start production environment
start_prod() {
    log "Starting production environment..."
    
    cd "$PROJECT_DIR"
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        warning ".env file not found, copying from .env.example"
        cp .env.example .env
        warning "Please update .env file with production values"
    fi
    
    # Start production services
    docker-compose --profile production up --build -d
    
    success "Production environment started"
    log "Services available at:"
    log "  - Application: http://localhost:8000"
    log "  - Nginx: http://localhost:80"
}

# Deploy to production
deploy() {
    log "Deploying to production..."
    
    # Build image
    build_image
    
    # Run tests
    run_tests
    
    # Push to registry if specified
    if [ -n "$REGISTRY" ]; then
        push_image
    fi
    
    # Start production environment
    start_prod
    
    success "Deployment completed successfully"
}

# Clean up Docker resources
clean_docker() {
    log "Cleaning up Docker resources..."
    
    # Stop and remove containers
    docker-compose down --remove-orphans || true
    docker-compose -f docker-compose.dev.yml down --remove-orphans || true
    
    # Remove images
    docker rmi "$IMAGE_NAME:$IMAGE_TAG" || true
    docker rmi "$IMAGE_NAME:latest" || true
    docker rmi "$IMAGE_NAME:test" || true
    
    # Clean up unused resources
    docker system prune -f
    
    success "Docker cleanup completed"
}

# Push image to registry
push_image() {
    if [ -z "$REGISTRY" ]; then
        error "Registry not specified. Use -r/--registry option."
        exit 1
    fi
    
    log "Pushing image to registry: $REGISTRY"
    
    # Tag for registry
    REGISTRY_IMAGE="$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
    docker tag "$IMAGE_NAME:$IMAGE_TAG" "$REGISTRY_IMAGE"
    
    # Push image
    if docker push "$REGISTRY_IMAGE"; then
        success "Image pushed successfully: $REGISTRY_IMAGE"
    else
        error "Failed to push image to registry"
        exit 1
    fi
}

# Pull image from registry
pull_image() {
    if [ -z "$REGISTRY" ]; then
        error "Registry not specified. Use -r/--registry option."
        exit 1
    fi
    
    log "Pulling image from registry: $REGISTRY"
    
    REGISTRY_IMAGE="$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
    
    if docker pull "$REGISTRY_IMAGE"; then
        # Tag as local image
        docker tag "$REGISTRY_IMAGE" "$IMAGE_NAME:$IMAGE_TAG"
        success "Image pulled successfully: $REGISTRY_IMAGE"
    else
        error "Failed to pull image from registry"
        exit 1
    fi
}

# Main execution
main() {
    log "Universal Consultant Intelligence Platform - Build Script"
    log "Command: $COMMAND"
    log "Environment: $ENVIRONMENT"
    log "Image: $IMAGE_NAME:$IMAGE_TAG"
    
    validate_environment
    
    case "$COMMAND" in
        build)
            build_image
            ;;
        test)
            run_tests
            ;;
        dev)
            start_dev
            ;;
        prod)
            start_prod
            ;;
        deploy)
            deploy
            ;;
        clean)
            clean_docker
            ;;
        push)
            push_image
            ;;
        pull)
            pull_image
            ;;
        *)
            error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Parse arguments and run
parse_args "$@"
main