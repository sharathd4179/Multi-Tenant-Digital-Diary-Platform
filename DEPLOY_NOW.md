# 🚀 Deploy to Production - Complete Guide

## ✅ Pre-Deployment Checklist

Let's verify everything is ready before deploying:

### 1. Code Status
- [x] ✅ CI/CD workflows exist (`.github/workflows/`)
- [x] ✅ Production docker-compose exists
- [x] ✅ Dockerfiles optimized
- [x] ✅ .env file exists (local)
- [ ] ⚠️ Git remote not configured yet
- [ ] ⚠️ Code not pushed to GitHub yet

### 2. Configuration
- [ ] ⚠️ GitHub Secrets need to be set
- [ ] ⚠️ Production .env.production needs to be created
- [x] ✅ Docker image names configured

### 3. Deployment Target
Choose your deployment method:
- [ ] Option A: GitHub Actions (Automatic - Recommended)
- [ ] Option B: Manual Server Deployment

---

## 🎯 Step-by-Step Deployment

### Phase 1: Prepare and Push Code (5 minutes)

#### Step 1: Initialize Git (if needed)

```powershell
# Check if git is initialized
if (-not (Test-Path .git)) {
    git init
    Write-Host "Git initialized" -ForegroundColor Green
} else {
    Write-Host "Git already initialized" -ForegroundColor Green
}
```

#### Step 2: Verify .env is Protected

```powershell
# Check .env is ignored
git check-ignore .env
# Should show: .env ✅

# Verify it's not tracked
git ls-files | Select-String "\.env"
# Should return nothing ✅
```

#### Step 3: Add and Commit All Files

```powershell
# Add all files (except .env which is ignored)
git add .

# Check what will be committed
git status
# .env should NOT appear ✅

# Commit
git commit -m "Production-ready: Optimized Docker builds, organized docs, CI/CD pipeline"
```

#### Step 4: Connect to GitHub

```powershell
# Add remote
git remote add origin https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git

# Or update if exists
git remote set-url origin https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git

# Verify
git remote -v
```

#### Step 5: Push to GitHub

```powershell
# Set main branch
git branch -M main

# Push
git push -u origin main
```

**If repository is not empty, you may need:**
```powershell
git push -u origin main --force
# (Be careful - this overwrites remote)
```

---

### Phase 2: Configure GitHub Secrets (2 minutes)

#### Step 6: Add OpenAI API Key Secret

1. Go to: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/settings/secrets/actions

2. Click **"New repository secret"**

3. Add:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** (Get from your `.env` file or OpenAI dashboard)

4. Click **"Add secret"**

✅ **Done!** Your secret is now encrypted and secure.

---

### Phase 3: Deploy to Production (Automatic)

#### Option A: Automatic via GitHub Actions (Recommended)

**Step 7: Tag and Deploy**

```powershell
# Create version tag
git tag v1.0.0

# Push tag (triggers production deployment)
git push origin v1.0.0
```

**What happens:**
1. ✅ GitHub Actions builds production images
2. ✅ Images pushed to GitHub Container Registry
3. ✅ Database migrations run
4. ✅ Health checks performed
5. ✅ Deployment completes

**Monitor:**
- Go to: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/actions
- Watch "CD - Continuous Deployment" run
- Wait for green checkmark ✅

#### Option B: Manual Server Deployment

**Step 7: Deploy to Your Server**

If deploying to your own server (VPS, cloud instance):

```bash
# On your server
git clone https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git
cd Multi-Tenant-Digital-Diary-Platform/multi-tenant-diary-assistant

# Create .env.production
nano .env.production
# Paste production environment variables

# Deploy
cd infra
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

---

## 🔍 Post-Deployment Verification

### Check 1: GitHub Actions

1. Go to: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/actions
2. Verify workflows completed successfully ✅
3. Check for any errors

### Check 2: Docker Images

1. Go to: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform?tab=packages
2. Verify images were built:
   - `multi-tenant-digital-diary-platform-backend`
   - `multi-tenant-digital-diary-platform-frontend`

### Check 3: Health Endpoints

If deployed to server:
```bash
curl http://your-server:8000/health/ready
# Should return: {"status": "ready"}
```

### Check 4: Application Access

- Frontend: http://your-server:8501
- API Docs: http://your-server:8000/docs
- Health: http://your-server:8000/health/

---

## 🆘 Troubleshooting

### "Git push fails"
- Check you're logged into GitHub
- Verify repository URL is correct
- Try: `git remote -v` to see remotes

### "GitHub Actions not running"
- Check Actions is enabled: Settings → Actions → General
- Verify workflow files exist
- Check you pushed to `main` branch

### "Deployment fails"
- Check GitHub Actions logs for errors
- Verify secrets are set correctly
- Check Docker image names match

### "Services not starting"
- Check logs: `docker-compose logs`
- Verify environment variables
- Check ports are available

---

## ✅ Success Indicators

You're successfully deployed when:

- [ ] ✅ Code pushed to GitHub
- [ ] ✅ GitHub Actions CI runs successfully
- [ ] ✅ Docker images built and pushed
- [ ] ✅ GitHub Secrets configured
- [ ] ✅ Production deployment completes
- [ ] ✅ Health checks pass
- [ ] ✅ Application accessible

---

## 🎉 You're Live!

Once all checks pass, your application is deployed and running!

**Next Steps:**
- Monitor logs for any issues
- Set up domain name (if needed)
- Configure SSL/HTTPS
- Set up monitoring/alerting

---

## 📚 Quick Reference

**Repository:** https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform

**Actions:** https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/actions

**Secrets:** https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/settings/secrets/actions

**Packages:** https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform?tab=packages

