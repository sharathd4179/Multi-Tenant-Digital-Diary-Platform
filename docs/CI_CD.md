# 🚀 CI/CD Setup

## Overview

The project uses GitHub Actions for automated testing and deployment.

## Workflows

### CI (Continuous Integration)

**Trigger:** Every push and pull request

**Actions:**
- Code linting (Black, Flake8)
- Type checking (MyPy)
- Unit tests
- Docker image builds

**File:** `.github/workflows/ci.yml`

### CD (Continuous Deployment)

**Trigger:** 
- Push to `main` → Staging
- Tag `v*` → Production

**Actions:**
- Build production images
- Push to GitHub Container Registry
- Run database migrations
- Deploy with health checks

**File:** `.github/workflows/deploy.yml`

## Setup

### 1. Add GitHub Secrets

Settings → Secrets → Actions:
- `OPENAI_API_KEY` - For tests

### 2. Push Code

```bash
git push origin main
```

### 3. Monitor

Go to: Actions tab to see workflows run

## Docker Images

Images are pushed to:
- `ghcr.io/sharathd4179/multi-tenant-digital-diary-platform-backend:latest`
- `ghcr.io/sharathd4179/multi-tenant-digital-diary-platform-frontend:latest`

## Deployment

### Staging (Automatic)
- Push to `main` branch
- Deploys automatically

### Production (Manual)
```bash
git tag v1.0.0
git push origin v1.0.0
```

See [Deployment Guide](DEPLOYMENT.md) for details.

