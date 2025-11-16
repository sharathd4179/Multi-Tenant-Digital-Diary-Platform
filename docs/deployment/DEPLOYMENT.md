# 🚀 Real-Time Deployment Guide

This guide explains how to set up and use the real-time CI/CD pipeline for the Multi-Tenant Diary Assistant.

## 📋 Overview

The deployment system includes:
- **GitHub Actions CI/CD**: Automated testing and deployment
- **Docker Compose Production**: Production-ready container orchestration
- **Automated Health Checks**: Zero-downtime deployments
- **Database Migrations**: Automatic schema updates

---

## 🔧 Setup Instructions

### 1. GitHub Actions Setup

#### Prerequisites
- GitHub repository (public or private)
- GitHub Actions enabled (enabled by default)

#### Required Secrets

Go to your repository → Settings → Secrets and variables → Actions, and add:

1. **OPENAI_API_KEY** (for tests)
   - Your OpenAI API key for running tests that require embeddings

2. **GITHUB_TOKEN** (automatically available)
   - Used for pushing Docker images to GitHub Container Registry

#### Optional Secrets (for cloud deployments)
- `DEPLOY_HOST`: SSH hostname for deployment server
- `DEPLOY_USER`: SSH username
- `DEPLOY_KEY`: SSH private key
- `DEPLOY_PATH`: Remote deployment path

### 2. Container Registry Setup

The workflows push images to GitHub Container Registry (`ghcr.io`). Images are automatically available at:
- `ghcr.io/YOUR_USERNAME/multi-tenant-diary-assistant-backend:latest`
- `ghcr.io/YOUR_USERNAME/multi-tenant-diary-assistant-frontend:latest`

To use these images:
1. Go to your repository → Packages
2. Configure package permissions (public or private)
3. Update `docker-compose.prod.yml` with your image names

### 3. Production Environment Configuration

#### Create `.env.production` file:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=diarydb

# Redis
REDIS_PASSWORD=your_redis_password_here

# JWT
JWT_SECRET_KEY=your_minimum_32_character_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# OpenAI (for RAG features)
OPENAI_API_KEY=sk-your-openai-api-key

# Application
ENVIRONMENT=production
LOG_LEVEL=info
RAG_CHUNK_SIZE=512
RAG_OVERLAP=50

# Docker Images (update with your registry)
BACKEND_IMAGE=ghcr.io/yourusername/multi-tenant-diary-assistant-backend:latest
FRONTEND_IMAGE=ghcr.io/yourusername/multi-tenant-diary-assistant-frontend:latest

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

**⚠️ Security Note**: Never commit `.env.production` to git! Add it to `.gitignore`.

---

## 🚀 Deployment Workflows

### Automatic Deployments

#### 1. **Staging Deployment** (Automatic)
- **Trigger**: Push to `main` branch
- **Workflow**: `.github/workflows/deploy.yml`
- **Actions**:
  - Builds Docker images
  - Pushes to container registry
  - Tags with branch name and commit SHA

#### 2. **Production Deployment** (Manual or Tag-based)
- **Trigger**: 
  - Push a tag starting with `v` (e.g., `v1.0.0`)
  - Manual workflow dispatch
- **Workflow**: `.github/workflows/deploy.yml`
- **Actions**:
  - Builds production images
  - Runs database migrations
  - Deploys with health checks
  - Sends notifications

### Manual Deployment

#### Using Docker Compose (Recommended for VPS/Server)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/multi-tenant-diary-assistant.git
cd multi-tenant-diary-assistant

# 2. Create .env.production file
cp .env.example .env.production
# Edit .env.production with your values

# 3. Make deploy script executable
chmod +x scripts/deploy.sh

# 4. Deploy
./scripts/deploy.sh production
```

#### Using Docker Compose Directly

```bash
cd multi-tenant-diary-assistant/infra
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 CI/CD Pipeline Flow

### Continuous Integration (CI)

**Trigger**: Every push and pull request

1. **Code Checkout**
2. **Linting** (Black, Flake8, MyPy)
3. **Testing**:
   - Unit tests
   - Integration tests
   - Coverage reports
4. **Docker Build** (test builds)
5. **Docker Compose Validation**

### Continuous Deployment (CD)

**Trigger**: Push to main (staging) or tag (production)

1. **Build Docker Images**
2. **Push to Registry**
3. **Deploy to Environment**
4. **Run Migrations**
5. **Health Checks**
6. **Notifications**

---

## 🔍 Monitoring Deployments

### Check Deployment Status

1. **GitHub Actions**: Go to repository → Actions tab
2. **View Logs**: Click on any workflow run to see detailed logs
3. **Health Endpoints**:
   - `http://your-server:8000/health/` - Basic health
   - `http://your-server:8000/health/ready` - Readiness (includes DB)
   - `http://your-server:8000/health/live` - Liveness

### View Container Logs

```bash
cd multi-tenant-diary-assistant/infra
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Check Container Status

```bash
docker-compose -f docker-compose.prod.yml ps
```

---

## 🛠️ Deployment Options

### Option 1: VPS/Cloud Server (DigitalOcean, AWS EC2, etc.)

1. Set up a server with Docker and Docker Compose
2. Clone repository
3. Configure `.env.production`
4. Run `./scripts/deploy.sh production`
5. Set up reverse proxy (Nginx) for HTTPS
6. Configure firewall rules

### Option 2: Cloud Platforms

#### AWS (ECS/Fargate)
- Use ECS task definitions
- Configure load balancer
- Set up RDS for PostgreSQL
- Use ElastiCache for Redis

#### Google Cloud (Cloud Run)
- Deploy containers to Cloud Run
- Use Cloud SQL for PostgreSQL
- Use Memorystore for Redis

#### Azure (Container Instances)
- Deploy to Azure Container Instances
- Use Azure Database for PostgreSQL
- Use Azure Cache for Redis

### Option 3: Kubernetes

1. Create Kubernetes manifests
2. Use Helm charts
3. Set up ingress controller
4. Configure persistent volumes for database and indexes

---

## 🔄 Rollback Procedure

If a deployment fails or needs to be rolled back:

```bash
# 1. Stop current deployment
cd multi-tenant-diary-assistant/infra
docker-compose -f docker-compose.prod.yml down

# 2. Pull previous image version
docker pull ghcr.io/yourusername/multi-tenant-diary-assistant-backend:previous-tag

# 3. Update docker-compose.prod.yml with previous image tag

# 4. Restart
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify health
curl http://localhost:8000/health/ready
```

---

## 🔐 Security Best Practices

1. **Secrets Management**:
   - Use GitHub Secrets for sensitive data
   - Never commit `.env.production`
   - Rotate JWT secrets regularly

2. **Network Security**:
   - Use HTTPS (configure SSL in Nginx)
   - Restrict database access (firewall rules)
   - Use strong passwords

3. **Container Security**:
   - Keep base images updated
   - Scan images for vulnerabilities
   - Use non-root users in containers

4. **Monitoring**:
   - Set up log aggregation
   - Monitor error rates
   - Alert on health check failures

---

## 📝 Deployment Checklist

Before deploying to production:

- [ ] All tests passing in CI
- [ ] `.env.production` configured
- [ ] Database backups configured
- [ ] SSL/TLS certificates ready
- [ ] Health check endpoints working
- [ ] Monitoring/alerting set up
- [ ] Rollback plan documented
- [ ] Team notified of deployment
- [ ] Database migrations tested
- [ ] Performance tested under load

---

## 🆘 Troubleshooting

### Deployment Fails

1. **Check GitHub Actions logs**: Repository → Actions
2. **Verify secrets**: Settings → Secrets
3. **Test locally**: Run `docker-compose -f docker-compose.prod.yml up`
4. **Check health endpoints**: `curl http://localhost:8000/health/ready`

### Images Not Building

1. **Check Dockerfile syntax**
2. **Verify build context paths**
3. **Check GitHub Actions build logs**

### Database Migration Issues

1. **Backup database first**
2. **Test migrations locally**
3. **Check Alembic version history**
4. **Rollback if needed**: `alembic downgrade -1`

### Health Checks Failing

1. **Check container logs**: `docker-compose logs`
2. **Verify environment variables**
3. **Check database connectivity**
4. **Verify Redis connectivity**

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## 💡 Tips

1. **Use semantic versioning** for production tags: `v1.0.0`, `v1.1.0`, etc.
2. **Test in staging first** before production
3. **Monitor deployments** closely for the first few minutes
4. **Keep deployment logs** for debugging
5. **Automate backups** before deployments
6. **Use feature flags** for gradual rollouts

---

## 🎯 Quick Start

```bash
# 1. Push code to trigger CI
git push origin main

# 2. Wait for CI to pass (check GitHub Actions)

# 3. Tag for production deployment
git tag v1.0.0
git push origin v1.0.0

# 4. Or deploy manually via GitHub Actions UI
# Go to Actions → Deploy → Run workflow
```

---

**Need help?** Check the logs, review the workflow files, or consult the troubleshooting section above.

