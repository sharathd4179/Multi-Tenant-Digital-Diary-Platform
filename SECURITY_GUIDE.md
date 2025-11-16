# 🔐 Security Guide - Keeping Your API Keys Safe

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

#### Verify It's Working

After adding the secret, your CI/CD workflow will automatically use it. Check:
- Go to **Actions** tab
- Run a workflow
- The `OPENAI_API_KEY` will be available but **never shown** in logs

---

### Method 2: Local .env File (For Development) ⭐ **RECOMMENDED**

**Use this for:** Running the app locally on your computer

#### Step 1: Create .env File

Create a file named `.env` in the `multi-tenant-diary-assistant` folder:

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

```powershell
# In PowerShell, verify:
Select-String -Path .gitignore -Pattern "\.env"
```

You should see `.env` listed. ✅

#### Step 3: Verify It's Not Committed

Before committing, check:

```powershell
# Check if .env would be committed
git status

# .env should NOT appear in the list
```

If `.env` appears, it means it's not ignored. Check your `.gitignore` file.

---

### Method 3: Production .env File (For Server Deployment)

**Use this for:** Deploying to your own server

#### Step 1: Create .env.production

Create `.env.production` in the project root:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=diarydb

# Redis
REDIS_PASSWORD=your_redis_password

# JWT Security (MUST be different from development!)
JWT_SECRET_KEY=your_production_secret_key_minimum_32_characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# OpenAI API Key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Application
ENVIRONMENT=production
LOG_LEVEL=info
RAG_CHUNK_SIZE=512
RAG_OVERLAP=50

# Docker Images
BACKEND_IMAGE=ghcr.io/sharathd4179/multi-tenant-digital-diary-platform-backend:latest
FRONTEND_IMAGE=ghcr.io/sharathd4179/multi-tenant-digital-diary-platform-frontend:latest

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

#### Step 2: Secure on Server

When deploying to a server:

```bash
# On your server, set proper permissions
chmod 600 .env.production

# Only owner can read/write
chown $USER:$USER .env.production
```

---

## 🔍 How to Verify Your Secret is Safe

### Check 1: Verify .env is in .gitignore

```powershell
# Check .gitignore includes .env
Get-Content .gitignore | Select-String "\.env"
```

Should show:
```
.env
.env.local
.env.production
```

### Check 2: Verify .env is NOT in Git

```powershell
# Check if .env is tracked by git
git ls-files | Select-String "\.env"
```

**Should return NOTHING** - if you see `.env`, it's being tracked! ⚠️

### Check 3: Search Code for Hardcoded Keys

```powershell
# Search for any hardcoded API keys (should find nothing)
Select-String -Path . -Pattern "sk-[a-zA-Z0-9]{20,}" -Recurse -Exclude "*.md","*.git*"
```

**Should return NOTHING** - if you see results, remove them! ⚠️

### Check 4: Verify GitHub Secrets

1. Go to: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/settings/secrets/actions
2. You should see `OPENAI_API_KEY` listed
3. **You cannot see the value** (this is correct - GitHub hides it)

---

## 🚨 What NOT to Do

### ❌ NEVER Do These:

1. **Don't commit .env files**
   ```powershell
   # BAD - Don't do this!
   git add .env
   git commit -m "Add API key"
   ```

2. **Don't hardcode keys in code**
   ```python
   # BAD - Never do this!
   openai_api_key = "sk-your-key-here"
   ```

3. **Don't share keys in chat/email**
   - Use secure methods only
   - Use GitHub Secrets or encrypted sharing

4. **Don't put keys in README or docs**
   - Even if you think it's "just an example"
   - Use placeholders: `sk-your-key-here`

5. **Don't commit keys accidentally**
   ```powershell
   # Always check before committing
   git status
   git diff
   ```

---

## ✅ Best Practices

### 1. Use Different Keys for Different Environments

- **Development:** One key (can be shared with team)
- **Staging:** Separate key
- **Production:** Separate key (most secure)

### 2. Rotate Keys Regularly

- Change your OpenAI API key every 3-6 months
- Update in GitHub Secrets and .env files
- Revoke old keys in OpenAI dashboard

### 3. Use Least Privilege

- Create API keys with minimal permissions needed
- Use separate keys for different services
- Monitor API usage regularly

### 4. Monitor for Leaks

- Set up alerts in OpenAI dashboard
- Monitor GitHub Actions logs (they hide secrets automatically)
- Use tools like `git-secrets` to prevent commits

### 5. Use Environment-Specific Files

```
.env                    # Local development (gitignored)
.env.production         # Production (gitignored)
.env.staging           # Staging (gitignored)
.env.example           # Template (can be committed)
```

---

## 🔧 Quick Setup Commands

### Add Secret to GitHub (One-Time)

1. Go to: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/settings/secrets/actions
2. Click **"New repository secret"**
3. Name: `OPENAI_API_KEY`
4. Value: Your actual key
5. Click **"Add secret"**

### Create Local .env File

```powershell
# Create .env file
@"
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/diarydb
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your_minimum_32_character_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
ENVIRONMENT=development
LOG_LEVEL=info
RAG_CHUNK_SIZE=512
RAG_OVERLAP=50
"@ | Out-File -FilePath .env -Encoding utf8

# Verify it's ignored
git status
# .env should NOT appear
```

### Verify Security

```powershell
# 1. Check .gitignore
Get-Content .gitignore | Select-String "\.env"

# 2. Check git tracking
git ls-files | Select-String "\.env"
# Should return nothing

# 3. Check for hardcoded keys
Select-String -Path . -Pattern "sk-[a-zA-Z0-9]{20,}" -Recurse -Exclude "*.md","*.git*","SECURITY_GUIDE.md"
# Should return nothing
```

---

## 🆘 If You Accidentally Committed a Secret

### Step 1: Remove from Git History

```powershell
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

### Step 3: Clean Git History (If Needed)

If the key was committed in the past:

```powershell
# Use git-filter-repo or BFG Repo-Cleaner
# This removes the key from all git history
```

**Note:** This rewrites history - coordinate with team if working together.

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

## 🎯 Summary

### For Local Development:
1. Create `.env` file with your API key
2. `.env` is automatically ignored by git ✅
3. App reads from `.env` automatically

### For CI/CD (GitHub Actions):
1. Add `OPENAI_API_KEY` to GitHub Secrets
2. Workflow automatically uses it
3. Key is encrypted and never shown in logs ✅

### For Production Server:
1. Create `.env.production` on server
2. Set secure file permissions (`chmod 600`)
3. Never commit to git ✅

---

## 💡 Pro Tips

1. **Use `.env.example`** - Create a template file (can be committed) showing what variables are needed, but without actual values

2. **Use different keys** - Development key can be shared, production key should be secret

3. **Monitor usage** - Check OpenAI dashboard regularly for unexpected usage

4. **Set up alerts** - Configure alerts in OpenAI dashboard for high usage

5. **Use key rotation** - Change keys periodically for security

---

## 🔗 Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OpenAI API Key Management](https://platform.openai.com/api-keys)
- [Environment Variables Best Practices](https://12factor.net/config)

---

## ✅ You're Secure!

If you followed this guide:
- ✅ Your API key is NOT in git
- ✅ Your API key is encrypted in GitHub Secrets
- ✅ Your API key is only in local .env files
- ✅ Your code is safe to push publicly

**Your secrets are protected! 🔐**

