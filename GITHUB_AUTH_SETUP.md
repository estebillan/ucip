# GitHub Authentication Setup for DigitalOcean App Platform

This guide will help you set up GitHub authentication to complete the deployment of the Universal Consultant Intelligence Platform.

## Prerequisites

1. **GitHub Repository Owner/Maintainer Access**: You must have Owner or Maintainer permissions for the `ravinderraju/clientraker` repository
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
4. Select the `ravinderraju/clientraker` repository

### Option B: Deploy Sample App First
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click **"Create App"**
3. Choose **"GitHub"** as source
4. You'll be prompted to authenticate with GitHub
5. Grant permissions to access your repositories
6. You can deploy a sample app just to complete the auth process

## Step 3: Configure Repository Secrets

1. Go to your GitHub repository: `https://github.com/ravinderraju/clientraker`
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

## Step 5: Create App Spec File

I'll create an App Spec file that DigitalOcean can use:

### `.do/app.yaml` (App Specification)
```yaml
name: consultant-intelligence-platform
services:
- name: api
  github:
    repo: ravinderraju/clientraker
    branch: main
    deploy_on_push: true
  dockerfile_path: Dockerfile.simple
  environment_slug: docker
  envs:
  - key: ENVIRONMENT
    value: production
  - key: DEBUG
    value: "false"
  instance_size_slug: basic-xxs
  instance_count: 1
  http_port: 8080
region: nyc
```

## Alternative: Static Site Deployment

If the Docker deployment continues to have issues, we can deploy as a static site:

```yaml
name: consultant-intelligence-platform
static_sites:
- name: frontend
  github:
    repo: ravinderraju/clientraker
    branch: main
    deploy_on_push: true
  source_dir: static-demo
  build_command: echo "Static site ready"
  output_dir: "."
  index_document: index.html
  error_document: index.html
region: nyc
```

## Troubleshooting

### If GitHub Authentication Fails:
1. Check repository permissions (must be Owner/Maintainer)
2. Try the one-click setup: https://cloud.digitalocean.com/apps/github/install
3. Revoke and re-grant GitHub permissions in your GitHub account settings

### If Token Issues:
1. Verify token has "Full Access" scope
2. Check token hasn't expired
3. Ensure token is correctly added to GitHub secrets

### Repository Access Issues:
1. Confirm repository name is exactly: `ravinderraju/clientraker`
2. Ensure repository is public or DigitalOcean has been granted access to private repos

## Next Steps

After completing GitHub authentication:

1. **Update the app**: Use the corrected app spec with GitHub integration
2. **Monitor deployment**: Check the deployment status in DigitalOcean dashboard
3. **Test the application**: Verify the deployed app is accessible
4. **Set up auto-deployment**: Commits to main branch will automatically trigger deployments

## Support Resources

- [DigitalOcean App Platform Documentation](https://docs.digitalocean.com/products/app-platform/)
- [GitHub Actions for App Platform](https://github.com/digitalocean/app_action)
- [DigitalOcean Community Support](https://www.digitalocean.com/community/questions)

Once GitHub authentication is set up, the Universal Consultant Intelligence Platform will be fully deployed and accessible!