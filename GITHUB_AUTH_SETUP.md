# GitHub Authentication Setup for DigitalOcean App Platform

This guide will help you set up GitHub authentication to complete the deployment of the Universal Consultant Intelligence Platform.

## Prerequisites

1. **GitHub Repository Owner Access**: You must have Owner permissions for the `estebillan/ucip` repository
2. **DigitalOcean Account**: Access to your DigitalOcean account
3. **Personal Access Token**: A DigitalOcean Personal Access Token

## Step 1: Create DigitalOcean Personal Access Token

1. Go to [DigitalOcean API Tokens](https://cloud.digitalocean.com/account/api/tokens)
2. Click **"Generate New Token"**
3. Name it: `App Platform GitHub Integration`
4. Select **"Full Access"** scope
5. Click **"Generate Token"**
6. **Copy and save the token** - you won't see it again!

## Step 2: Initial GitHub Authentication

### Option A: One-Click Authentication Setup
1. Visit: https://cloud.digitalocean.com/apps/github/install
2. This will walk you through the GitHub authentication process
3. Grant DigitalOcean App Platform access to your GitHub account
4. Select the `estebillan/ucip` repository

### Option B: Deploy Sample App First
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click **"Create App"**
3. Choose **"GitHub"** as source
4. You'll be prompted to authenticate with GitHub
5. Grant permissions to access your repositories
6. You can deploy a sample app just to complete the auth process

## Step 3: Configure Repository Secrets

1. Go to your GitHub repository: `https://github.com/estebillan/ucip`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Name: `DIGITALOCEAN_ACCESS_TOKEN`
5. Value: Paste your DigitalOcean Personal Access Token
6. Click **"Add secret"**

## Step 4: Update App Deployment

Once GitHub authentication is complete, we can update the app with proper GitHub integration:

```bash
# Use the DigitalOcean CLI to update the app
doctl apps update 5698aa9c-1da8-40a4-8a48-d1a56bd883ee --spec .do/app.yaml
```

## Step 5: Repository Information

### Repository Details:
- **Name**: `estebillan/ucip`
- **Full Name**: Universal Consultant Intelligence Platform
- **URL**: https://github.com/estebillan/ucip
- **Purpose**: AI-powered research and intelligence platform for consultants

### App Specification
The `.do/app.yaml` file contains the complete deployment configuration:
```yaml
name: consultant-intelligence-platform
static_sites:
- name: demo-site
  github:
    repo: estebillan/ucip
    branch: main
    deploy_on_push: true
  source_dir: static-demo
```

## Alternative: Static Site Deployment

The current configuration deploys as a static site for reliability:
- **Source Directory**: `static-demo/`
- **Index Page**: Professional showcase of the platform
- **Features**: Interactive demo of all platform capabilities
- **Auto-deploy**: Enabled on pushes to main branch

## Troubleshooting

### If GitHub Authentication Fails:
1. Check repository permissions (must be Owner of estebillan/ucip)
2. Try the one-click setup: https://cloud.digitalocean.com/apps/github/install
3. Revoke and re-grant GitHub permissions in your GitHub account settings

### If Token Issues:
1. Verify token has "Full Access" scope
2. Check token hasn't expired
3. Ensure token is correctly added to GitHub secrets

### Repository Access Issues:
1. Confirm repository name is exactly: `estebillan/ucip`
2. Ensure repository is public or DigitalOcean has been granted access to private repos
3. Verify you have Owner permissions on the repository

## Next Steps

After completing GitHub authentication:

1. **Update the app**: Use the corrected app spec with GitHub integration
2. **Monitor deployment**: Check the deployment status in DigitalOcean dashboard
3. **Test the application**: Verify the deployed app is accessible
4. **Set up auto-deployment**: Commits to main branch will automatically trigger deployments

## Platform Features Showcase

The deployed static site will showcase:
- 🧠 **AI-Powered Research**: OpenAI GPT-4 integration
- 🔍 **Smart Scraping**: Beautiful Soup web intelligence
- 📊 **Signal Detection**: Intelligent opportunity identification
- 📑 **Report Generation**: Professional PDF creation
- 🏗️ **Full Stack**: FastAPI + TypeScript + PostgreSQL + Redis

## Support Resources

- [DigitalOcean App Platform Documentation](https://docs.digitalocean.com/products/app-platform/)
- [GitHub Actions for App Platform](https://github.com/digitalocean/app_action)
- [DigitalOcean Community Support](https://www.digitalocean.com/community/questions)
- [Repository URL](https://github.com/estebillan/ucip)

Once GitHub authentication is set up, the Universal Consultant Intelligence Platform will be fully deployed and accessible!