# ⚡ Quick Deployment Guide

## 🚀 Real-Time Deployment is Ready!

Your application now has a complete CI/CD pipeline set up. Here's how to use it:

---

## 📦 What Was Created

1. **GitHub Actions CI** (`.github/workflows/ci.yml`)
   - Automated testing on every push
   - Code linting and type checking
   - Docker image building

2. **GitHub Actions CD** (`.github/workflows/deploy.yml`)
   - Automatic staging deployment on `main` branch
   - Production deployment on version tags
   - Manual deployment option

3. **Production Docker Compose** (`infra/docker-compose.prod.yml`)
   - Production-ready configuration
   - Health checks
   - Resource limits
   - Nginx reverse proxy

4. **Deployment Script** (`scripts/deploy.sh`)
   - One-command deployment
   - Automatic health checks
   - Migration handling

5. **Nginx Configuration** (`infra/nginx.conf`)
   - Reverse proxy setup
   - Rate limiting
   - Security headers

---

## 🎯 Quick Start (3 Steps)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

This automatically:
- ✅ Runs tests
- ✅ Builds Docker images
- ✅ Deploys to staging (if configured)

### Step 2: Configure Secrets

Go to your GitHub repository:
1. Settings → Secrets and variables → Actions
2. Add `OPENAI_API_KEY` (for tests)

### Step 3: Deploy to Production

**Option A: Tag-based (Recommended)**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**Option B: Manual**
1. Go to GitHub → Actions
2. Select "CD - Continuous Deployment"
3. Click "Run workflow"
4. Choose environment (staging/production)

---

## 🖥️ Local Production Deployment

If deploying to your own server:

```bash
# 1. Create production environment file
cp .env.production.example .env.production
# Edit .env.production with your values

# 2. Deploy
cd multi-tenant-diary-assistant
./scripts/deploy.sh production
```

---

## 📊 Deployment Status

Check deployment status:
- **GitHub Actions**: Repository → Actions tab
- **Health Checks**: `http://your-server:8000/health/ready`
- **Container Logs**: `docker-compose -f infra/docker-compose.prod.yml logs -f`

---

## 🔧 Configuration

### Update Image Names

Edit `infra/docker-compose.prod.yml`:
```yaml
backend:
  image: ghcr.io/YOUR_USERNAME/multi-tenant-diary-assistant-backend:latest
```

### Environment Variables

Create `.env.production` with:
- Database credentials
- JWT secret (min 32 chars)
- OpenAI API key
- Redis password

---

## 📚 Full Documentation

See `DEPLOYMENT.md` for:
- Detailed setup instructions
- Cloud platform guides
- Troubleshooting
- Security best practices

---

## ✅ What Happens Automatically

### On Every Push:
1. ✅ Code linting (Black, Flake8)
2. ✅ Unit & integration tests
3. ✅ Docker image builds
4. ✅ Coverage reports

### On Push to `main`:
1. ✅ Build production images
2. ✅ Push to GitHub Container Registry
3. ✅ Tag with commit SHA

### On Version Tag (`v*`):
1. ✅ Build production images
2. ✅ Run database migrations
3. ✅ Deploy to production
4. ✅ Health checks
5. ✅ Notifications

---

## 🎉 You're All Set!

Your application now has:
- ✅ Automated testing
- ✅ Continuous integration
- ✅ Automated deployments
- ✅ Production-ready configuration
- ✅ Health monitoring
- ✅ Zero-downtime deployments

**Next**: Push your code and watch it deploy automatically! 🚀

