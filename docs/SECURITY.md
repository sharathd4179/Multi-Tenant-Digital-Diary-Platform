# 🔐 Security Guide

## ⚠️ CRITICAL: Never Commit Secrets to Git!

Your OpenAI API key is **sensitive information**. This guide shows you how to keep it secure.

---

## ✅ What's Already Protected

Your project is already configured to protect secrets:

- ✅ `.gitignore` excludes all `.env` files
- ✅ Environment variables are loaded securely
- ✅ No secrets are hardcoded in the code

---

## 🎯 Three Ways to Store Your OpenAI API Key Securely

### Method 1: GitHub Secrets (For CI/CD) ⭐ **RECOMMENDED**

**Use this for:** Automated deployments and CI/CD pipelines

#### Step 1: Add Secret to GitHub

1. Go to your repository: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions**
4. Click **"New repository secret"**
5. Fill in:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** `sk-your-actual-openai-api-key-here`
6. Click **"Add secret"**

✅ **Done!** Your key is now encrypted and stored securely by GitHub.

#### How It Works

- GitHub encrypts the secret
- Only accessible during GitHub Actions workflows
- Never visible in logs or code
- Can't be accessed by anyone else

---

### Method 2: Local .env File (For Development) ⭐ **RECOMMENDED**

**Use this for:** Running the app locally on your computer

#### Step 1: Create .env File

Create a file named `.env` in the project root:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/diarydb

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Security
JWT_SECRET_KEY=your_minimum_32_character_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# OpenAI API Key - YOUR SECRET KEY GOES HERE
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Application
ENVIRONMENT=development
LOG_LEVEL=info
RAG_CHUNK_SIZE=512
RAG_OVERLAP=50
```

#### Step 2: Verify .env is Ignored

Check that `.env` is in `.gitignore`:

```bash
git check-ignore .env  # Should return: .env
git ls-files | grep .env  # Should return nothing
```

---

### Method 3: Production .env File (For Server Deployment)

**Use this for:** Deploying to your own server

Create `.env.production` in the project root with production values. Set secure permissions:

```bash
chmod 600 .env.production
chown $USER:$USER .env.production
```

---

## 🔍 How to Verify Your Secret is Safe

### Check 1: Verify .env is in .gitignore

```bash
git check-ignore .env  # Should return: .env
```

### Check 2: Verify .env is NOT in Git

```bash
git ls-files | grep .env  # Should return nothing
```

**Should return NOTHING** - if you see `.env`, it's being tracked! ⚠️

### Check 3: Search Code for Hardcoded Keys

```bash
grep -r "sk-[a-zA-Z0-9]\{20,\}" --exclude-dir=.git --exclude="*.md"
```

**Should return NOTHING** - if you see results, remove them! ⚠️

---

## 🚨 What NOT to Do

### ❌ NEVER Do These:

1. **Don't commit .env files**
2. **Don't hardcode keys in code**
3. **Don't share keys in chat/email**
4. **Don't put keys in README or docs**
5. **Don't commit keys accidentally**

---

## ✅ Best Practices

1. **Use Different Keys for Different Environments**
   - Development: One key (can be shared with team)
   - Staging: Separate key
   - Production: Separate key (most secure)

2. **Rotate Keys Regularly**
   - Change your OpenAI API key every 3-6 months
   - Update in GitHub Secrets and .env files
   - Revoke old keys in OpenAI dashboard

3. **Use Least Privilege**
   - Create API keys with minimal permissions needed
   - Use separate keys for different services
   - Monitor API usage regularly

4. **Monitor for Leaks**
   - Set up alerts in OpenAI dashboard
   - Monitor GitHub Actions logs (they hide secrets automatically)
   - Use tools like `git-secrets` to prevent commits

---

## Production Security

- Use strong `JWT_SECRET_KEY` (32+ characters)
- Enable HTTPS/TLS
- Restrict CORS origins
- Use environment-specific configs
- Enable rate limiting
- Monitor logs for suspicious activity

---

## 📋 Security Checklist

Before pushing code:

- [ ] ✅ `.env` file exists locally but is NOT committed
- [ ] ✅ `.env` is in `.gitignore`
- [ ] ✅ No hardcoded API keys in code
- [ ] ✅ GitHub Secrets configured (for CI/CD)
- [ ] ✅ `.env.production` created (for server deployment)
- [ ] ✅ Different keys for dev/staging/production
- [ ] ✅ Verified `git status` shows no .env files
- [ ] ✅ Verified `git ls-files` shows no .env files

---

## 🆘 If You Accidentally Committed a Secret

### Step 1: Remove from Git History

```bash
# Remove file from git (but keep local copy)
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from git tracking"

# Push
git push origin main
```

### Step 2: Rotate the Key

1. Go to OpenAI dashboard
2. Revoke the exposed key
3. Create a new key
4. Update in GitHub Secrets and .env files

---

## See Also

- [API Key Setup](API_KEY_SETUP.md)
- [Deployment Guide](deployment/PRODUCTION.md)
- [Quick Start Guide](QUICK_START.md)

