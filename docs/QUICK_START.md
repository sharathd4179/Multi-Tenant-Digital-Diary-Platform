# ⚡ Quick Start Guide

Get your Multi-Tenant Diary Assistant running in 5 minutes!

## Prerequisites

- Docker and Docker Compose
- OpenAI API key (optional, for RAG features)
- Git (for deployment)

---

## 🚀 Quick Start (Choose Your Path)

### Path A: Run Locally 🏠

Follow the "Local Setup" section below.

### Path B: Deploy to Production ⚡

1. Push to GitHub (triggers CI/CD automatically)
2. Configure GitHub Secrets (see [Security Guide](SECURITY.md))
3. Tag a version for production deployment

See [Deployment Guide](deployment/PRODUCTION.md) for details.

---

## Local Setup

### 1. Create Environment File

Create `.env` in project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/diarydb
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your_minimum_32_character_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200
OPENAI_API_KEY=sk-your-openai-api-key-here
ENVIRONMENT=development
LOG_LEVEL=info
RAG_CHUNK_SIZE=512
RAG_OVERLAP=50
```

**Important:** The `.env` file is already in `.gitignore` - it will NOT be committed to git.

### 2. Start Services

```bash
cd infrastructure/docker
docker-compose up --build
```

Or use Docker Compose from project root:

```bash
docker-compose -f infrastructure/docker/docker-compose.yml up --build
```

### 3. Access Application

- **Frontend:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health/

---

## First Steps

1. **Create a Tenant:**
   - Go to http://localhost:8000/docs
   - Use `/auth/register-tenant` endpoint
   - Save your `tenant_id`

2. **Login:**
   - Go to http://localhost:8501
   - Enter tenant_id, username, password

3. **Create Notes:**
   - Use the Diary section
   - Add tags for organization

4. **Search:**
   - Use semantic search (requires FAISS indexes)
   - Build indexes: `python scripts/create_faiss_index.py`

---

## 🎯 What Happens When You Push Code?

### Automatic (Every Push to `main`):
1. ✅ **Tests Run** - All your tests execute
2. ✅ **Code Checked** - Linting and type checking
3. ✅ **Docker Built** - Images are built
4. ✅ **Deployed** - Staging deployment (if configured)

### Manual (Tag a Version):
1. ✅ **Production Build** - Production images created
2. ✅ **Migrations Run** - Database updated
3. ✅ **Health Checks** - Services verified
4. ✅ **Live!** - Your app is deployed

---

## 🆘 Common Issues & Solutions

### "Git not initialized"
```bash
git init
git add .
git commit -m "Initial commit"
```

### "Docker not running"
- Install Docker Desktop
- Make sure it's running (check system tray)

### "Port already in use"
```bash
# Check what's using the port
netstat -ano | findstr :8000
# Stop the process or change port in docker-compose.yml
```

### "GitHub Actions not running"
1. Check Actions is enabled: Settings → Actions → General
2. Check secrets are set: Settings → Secrets → Actions
3. Check workflow files exist: `.github/workflows/`

---

## 📚 Next Steps

- [Setup Guide](SETUP.md) - Detailed configuration
- [Usage Guide](guides/USAGE.md) - Application features
- [Deployment Guide](deployment/PRODUCTION.md) - Production deployment
- [Security Guide](SECURITY.md) - API key management
- [CI/CD Guide](CI_CD.md) - Continuous integration

---

## ✅ Success Checklist

You're ready when:

- [ ] ✅ Code pushed to GitHub
- [ ] ✅ GitHub Actions runs successfully
- [ ] ✅ Docker images build
- [ ] ✅ Tests pass
- [ ] ✅ Local app runs (if testing locally)

---

## 💡 Pro Tips

1. **Start Small** - Test locally first
2. **Read Logs** - GitHub Actions shows detailed logs
3. **Check Health** - Use `/health/ready` endpoint
4. **Version Tags** - Use semantic versioning: `v1.0.0`
5. **Keep Secrets Safe** - Never commit `.env` files

---

**Ready to start? Follow the steps above! 🚀**

