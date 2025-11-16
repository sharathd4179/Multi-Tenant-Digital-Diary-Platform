# 🎯 Step-by-Step Deployment Guide

This guide will walk you through deploying your Multi-Tenant Diary Assistant in real-time, step by step.

---

## 📋 Prerequisites Checklist

Before we start, make sure you have:

- [ ] **Git** installed and configured
- [ ] **Docker** and **Docker Compose** installed
- [ ] **GitHub account** (for CI/CD)
- [ ] **GitHub repository** (or create one)
- [ ] **OpenAI API key** (for RAG features - optional but recommended)

---

## 🚀 Part 1: Initial Setup (One-Time)

### Step 1: Initialize Git Repository (if not already done)

```powershell
# Navigate to your project
cd multi-tenant-diary-assistant

# Check if git is initialized
git status

# If not initialized, run:
git init
git add .
git commit -m "Initial commit: Multi-tenant diary assistant with CI/CD"
```

### Step 2: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon → **"New repository"**
3. Name it: `multi-tenant-diary-assistant`
4. Choose **Public** or **Private**
5. **Don't** initialize with README (you already have one)
6. Click **"Create repository"**

### Step 3: Connect Local Repository to GitHub

```powershell
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/multi-tenant-diary-assistant.git

# Verify it's added
git remote -v

# Push your code
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

---

## 🔐 Part 2: Configure Secrets

### Step 4: Set Up GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add these secrets:

   **Secret 1: OPENAI_API_KEY**
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (starts with `sk-`)
   - Get it from: https://platform.openai.com/api-keys

   **Secret 2: (Optional) DEPLOY_HOST**
   - Only if deploying to a remote server
   - Name: `DEPLOY_HOST`
   - Value: Your server IP or domain

   **Secret 3: (Optional) DEPLOY_USER**
   - Only if deploying to a remote server
   - Name: `DEPLOY_USER`
   - Value: SSH username (e.g., `ubuntu`, `root`)

---

## 🐳 Part 3: Local Development Setup

### Step 5: Create Environment File

```powershell
# Navigate to project root
cd multi-tenant-diary-assistant

# Create .env file (copy from example if exists, or create new)
# Create .env file with these contents:
```

Create a file named `.env` in the `multi-tenant-diary-assistant` folder with:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/diarydb

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Security
JWT_SECRET_KEY=your_minimum_32_character_secret_key_change_this_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# OpenAI (Optional - for RAG features)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Application
ENVIRONMENT=development
LOG_LEVEL=info
RAG_CHUNK_SIZE=512
RAG_OVERLAP=50
```

**⚠️ Important**: Replace `JWT_SECRET_KEY` with a random 32+ character string!

### Step 6: Test Local Deployment

```powershell
# Navigate to infra directory
cd infra

# Start all services
docker-compose up --build

# Wait for services to start (you'll see logs)
# Press Ctrl+C to stop when done testing
```

**Expected output:**
- ✅ Database starts on port 5432
- ✅ Redis starts on port 6379
- ✅ Backend starts on port 8000
- ✅ Frontend starts on port 8501

**Test it:**
- Open browser: http://localhost:8501
- API docs: http://localhost:8000/docs

---

## 🚀 Part 4: Set Up Real-Time Deployment

### Step 7: Update Docker Image Names

Edit `infra/docker-compose.prod.yml`:

Find these lines (around line 30-35):
```yaml
backend:
  image: ${BACKEND_IMAGE:-ghcr.io/yourusername/multi-tenant-diary-assistant-backend:latest}
```

Replace `yourusername` with your GitHub username:
```yaml
backend:
  image: ${BACKEND_IMAGE:-ghcr.io/YOUR_GITHUB_USERNAME/multi-tenant-diary-assistant-backend:latest}
```

Do the same for frontend (around line 50):
```yaml
frontend:
  image: ${FRONTEND_IMAGE:-ghcr.io/YOUR_GITHUB_USERNAME/multi-tenant-diary-assistant-frontend:latest}
```

### Step 8: Commit and Push CI/CD Files

```powershell
# Make sure you're in the project root
cd multi-tenant-diary-assistant

# Check what files were added
git status

# Add all new files
git add .

# Commit
git commit -m "Add CI/CD pipeline for real-time deployment"

# Push to GitHub
git push origin main
```

**🎉 This triggers your first CI run!**

### Step 9: Monitor Your First CI Run

1. Go to your GitHub repository
2. Click the **"Actions"** tab
3. You should see a workflow running: **"CI - Continuous Integration"**
4. Click on it to see:
   - ✅ Code checkout
   - ✅ Python setup
   - ✅ Linting
   - ✅ Tests
   - ✅ Docker builds

**Wait for it to complete** (usually 3-5 minutes)

---

## 📦 Part 5: First Deployment

### Step 10: Create Production Environment File

```powershell
# Create production environment file
# Copy .env.production.example to .env.production
# Or create new file:
```

Create `.env.production` in `multi-tenant-diary-assistant` folder:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_production_password_here
POSTGRES_DB=diarydb

# Redis
REDIS_PASSWORD=your_redis_password_here

# JWT Security (MUST be different from development!)
JWT_SECRET_KEY=your_production_secret_key_minimum_32_characters_long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# Application
ENVIRONMENT=production
LOG_LEVEL=info
RAG_CHUNK_SIZE=512
RAG_OVERLAP=50

# Docker Images (Update with YOUR GitHub username)
BACKEND_IMAGE=ghcr.io/YOUR_GITHUB_USERNAME/multi-tenant-diary-assistant-backend:latest
FRONTEND_IMAGE=ghcr.io/YOUR_GITHUB_USERNAME/multi-tenant-diary-assistant-frontend:latest

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

**⚠️ Security**: Never commit `.env.production` to git! It's already in `.gitignore`.

### Step 11: Deploy to Production (Tag-Based)

```powershell
# Create a version tag
git tag v1.0.0

# Push the tag (this triggers production deployment)
git push origin v1.0.0
```

**What happens:**
1. GitHub Actions builds production images
2. Pushes to GitHub Container Registry
3. Runs database migrations
4. Deploys to production
5. Runs health checks

**Monitor it:**
- Go to **Actions** tab
- Click on **"CD - Continuous Deployment"**
- Watch the deployment progress

---

## 🖥️ Part 6: Deploy to Your Server (Optional)

If you want to deploy to your own server (VPS, cloud instance, etc.):

### Step 12: Prepare Your Server

**Requirements:**
- Linux server (Ubuntu 20.04+ recommended)
- Docker and Docker Compose installed
- Ports 80, 443, 8000, 8501 open

**On your server, run:**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

### Step 13: Clone Repository on Server

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/multi-tenant-diary-assistant.git
cd multi-tenant-diary-assistant/multi-tenant-diary-assistant

# Create .env.production file
nano .env.production
# Paste your production environment variables
# Save and exit (Ctrl+X, Y, Enter)
```

### Step 14: Deploy on Server

```bash
# Make deploy script executable
chmod +x scripts/deploy.sh

# Deploy
./scripts/deploy.sh production
```

**Or manually:**

```bash
cd infra
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### Step 15: Verify Deployment

```bash
# Check if services are running
docker-compose -f infra/docker-compose.prod.yml ps

# Check health
curl http://localhost:8000/health/ready

# View logs
docker-compose -f infra/docker-compose.prod.yml logs -f
```

---

## 🔄 Part 7: Ongoing Deployments

### For Future Updates:

**Every time you make changes:**

```powershell
# 1. Make your code changes
# 2. Test locally
cd infra
docker-compose up

# 3. Commit and push
git add .
git commit -m "Your change description"
git push origin main

# 4. Automatic deployment happens!
# - CI runs automatically
# - Staging deploys automatically
```

**For production releases:**

```powershell
# 1. Tag new version
git tag v1.1.0

# 2. Push tag
git push origin v1.1.0

# 3. Production deployment happens automatically!
```

---

## 🎯 Quick Reference Commands

### Local Development
```powershell
# Start services
cd infra
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
```

### Deployment
```powershell
# Deploy locally
./scripts/deploy.sh production

# Check status
docker-compose -f infra/docker-compose.prod.yml ps

# View logs
docker-compose -f infra/docker-compose.prod.yml logs -f
```

### Git Workflow
```powershell
# Daily workflow
git add .
git commit -m "Description"
git push origin main

# Production release
git tag v1.0.0
git push origin v1.0.0
```

---

## 🆘 Troubleshooting

### CI/CD Not Running?

1. **Check GitHub Actions is enabled:**
   - Repository → Settings → Actions → General
   - Ensure "Allow all actions" is selected

2. **Check secrets are set:**
   - Settings → Secrets → Actions
   - Verify `OPENAI_API_KEY` exists

3. **Check workflow files exist:**
   - Verify `.github/workflows/ci.yml` exists
   - Verify `.github/workflows/deploy.yml` exists

### Deployment Fails?

1. **Check GitHub Actions logs:**
   - Go to Actions tab
   - Click on failed workflow
   - Check error messages

2. **Verify environment variables:**
   - Check `.env.production` exists
   - Verify all required variables are set

3. **Check Docker images:**
   - Go to repository → Packages
   - Verify images were built

### Services Not Starting?

1. **Check ports are available:**
   ```powershell
   netstat -ano | findstr :8000
   netstat -ano | findstr :8501
   ```

2. **Check Docker is running:**
   ```powershell
   docker ps
   ```

3. **Check logs:**
   ```powershell
   docker-compose -f infra/docker-compose.prod.yml logs
   ```

---

## ✅ Success Checklist

You're successfully deployed when:

- [ ] ✅ GitHub Actions CI runs on every push
- [ ] ✅ Docker images build successfully
- [ ] ✅ Tests pass
- [ ] ✅ Images pushed to GitHub Container Registry
- [ ] ✅ Production deployment completes
- [ ] ✅ Health checks pass: `http://your-server:8000/health/ready`
- [ ] ✅ Frontend accessible: `http://your-server:8501`
- [ ] ✅ API docs accessible: `http://your-server:8000/docs`

---

## 📚 Next Steps

1. **Set up monitoring** (optional):
   - Add Sentry for error tracking
   - Set up uptime monitoring
   - Configure log aggregation

2. **Set up SSL/HTTPS** (recommended):
   - Get SSL certificate (Let's Encrypt)
   - Configure Nginx for HTTPS
   - Update `nginx.conf`

3. **Set up backups** (important):
   - Database backups
   - FAISS index backups
   - Automated backup schedule

4. **Scale up** (when needed):
   - Add more backend instances
   - Set up load balancer
   - Use managed database (RDS, Cloud SQL)

---

## 💡 Tips

1. **Always test locally first** before pushing
2. **Use semantic versioning** for tags: `v1.0.0`, `v1.1.0`, `v2.0.0`
3. **Monitor deployments** for the first few minutes
4. **Keep `.env.production` secure** - never commit it
5. **Review GitHub Actions logs** if something fails
6. **Start with staging** before production deployments

---

## 🎉 Congratulations!

You now have a fully automated, real-time deployment pipeline! 

**Every push to `main`** → Automatic testing and staging deployment  
**Every version tag** → Automatic production deployment

Your application is production-ready! 🚀

---

**Need help?** Check:
- `DEPLOYMENT.md` - Detailed deployment guide
- `QUICK_DEPLOY.md` - Quick reference
- GitHub Actions logs - For specific errors

