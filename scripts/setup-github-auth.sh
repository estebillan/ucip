#!/bin/bash
# Universal Consultant Intelligence Platform - GitHub Authentication Setup
# Helper script for setting up GitHub authentication with DigitalOcean App Platform

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] [SETUP]${NC} $1"
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

# Main setup function
setup_github_auth() {
    log "🧠 Universal Consultant Intelligence Platform - GitHub Authentication Setup"
    echo
    
    log "This script will help you set up GitHub authentication for DigitalOcean App Platform"
    echo
    
    # Step 1: Check prerequisites
    log "📋 Step 1: Checking prerequisites..."
    
    if ! command -v doctl &> /dev/null; then
        warning "doctl (DigitalOcean CLI) is not installed"
        log "Install it from: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        log "This is optional but recommended for advanced management"
    else
        success "doctl CLI found"
    fi
    
    if ! command -v git &> /dev/null; then
        error "git is not installed. Please install git first."
        exit 1
    else
        success "git found"
    fi
    
    # Step 2: GitHub repository check
    log "📂 Step 2: Checking GitHub repository..."
    
    CURRENT_REPO=$(git config --get remote.origin.url 2>/dev/null || echo "")
    if [[ $CURRENT_REPO == *"estebillan/ucip"* ]]; then
        success "Correct repository: $CURRENT_REPO"
    else
        warning "Repository might not be correctly configured"
        log "Expected: estebillan/ucip"
        log "Current: $CURRENT_REPO"
    fi
    
    # Step 3: Authentication instructions
    log "🔐 Step 3: GitHub Authentication Setup"
    echo
    echo "Follow these steps to complete GitHub authentication:"
    echo
    echo "1. 📱 Create DigitalOcean Personal Access Token:"
    echo "   → Go to: https://cloud.digitalocean.com/account/api/tokens"
    echo "   → Click 'Generate New Token'"
    echo "   → Name: 'App Platform GitHub Integration'"
    echo "   → Scope: 'Full Access'"
    echo "   → Save the token securely!"
    echo
    echo "2. 🔗 Complete GitHub Authentication:"
    echo "   → Visit: https://cloud.digitalocean.com/apps/github/install"
    echo "   → Grant DigitalOcean access to your GitHub account"
    echo "   → Select the 'estebillan/ucip' repository"
    echo
    echo "3. 🔑 Add Token to GitHub Secrets:"
    echo "   → Go to: https://github.com/estebillan/ucip/settings/secrets/actions"
    echo "   → Click 'New repository secret'"
    echo "   → Name: 'DIGITALOCEAN_ACCESS_TOKEN'"
    echo "   → Value: [Paste your DigitalOcean token]"
    echo
    
    # Step 4: Deployment options
    log "🚀 Step 4: Deployment Options"
    echo
    echo "After completing authentication, you can:"
    echo
    echo "A. 🏃‍♂️ Quick Deploy (Static Site):"
    echo "   → Push changes to main branch"
    echo "   → GitHub Actions will auto-deploy"
    echo "   → App will be available at DigitalOcean-provided URL"
    echo
    echo "B. 🔧 Manual Deploy:"
    echo "   → Use: doctl apps update 5698aa9c-1da8-40a4-8a48-d1a56bd883ee --spec .do/app.yaml"
    echo "   → Monitor: https://cloud.digitalocean.com/apps"
    echo
    echo "C. 🔄 Full Application Deploy:"
    echo "   → Edit .do/app.yaml to uncomment service section"
    echo "   → Configure environment variables"
    echo "   → Deploy full FastAPI application"
    echo
    
    # Step 5: Verification
    log "✅ Step 5: Verification"
    echo
    echo "After deployment, verify:"
    echo "• ✅ App appears in DigitalOcean App Platform dashboard"
    echo "• ✅ GitHub repository is connected"
    echo "• ✅ Auto-deploy is enabled"
    echo "• ✅ Application is accessible via provided URL"
    echo
    
    success "GitHub Authentication Setup Guide Complete!"
    echo
    log "📚 For detailed instructions, see: GITHUB_AUTH_SETUP.md"
    log "🐞 For issues, check: https://www.digitalocean.com/community/questions"
    log "📖 Full documentation: https://docs.digitalocean.com/products/app-platform/"
}

# Run setup
setup_github_auth