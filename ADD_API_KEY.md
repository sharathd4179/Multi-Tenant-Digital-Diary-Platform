# 🔑 Quick Guide: Adding Your OpenAI API Key Securely

## ⚡ Fast Setup (2 Minutes)

### Step 1: Add to GitHub Secrets (For CI/CD)

1. **Go to:** https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/settings/secrets/actions

2. **Click:** "New repository secret"

3. **Enter:**
   - **Name:** `OPENAI_API_KEY`
   - **Value:** `sk-your-actual-openai-api-key-here` (paste your real key)

4. **Click:** "Add secret"

✅ **Done!** Your key is now encrypted and secure for CI/CD.

---

### Step 2: Add to Local .env File (For Development)

1. **Create file:** `.env` in `multi-tenant-diary-assistant` folder

2. **Add this content:**
   ```env
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
   ```

3. **Replace** `sk-your-actual-openai-api-key-here` with your real key

4. **Verify it's ignored:**
   ```powershell
   git status
   # .env should NOT appear in the list
   ```

✅ **Done!** Your key is secure locally.

---

## 🔍 Verify It's Safe

```powershell
# Check .env is NOT tracked by git
git ls-files | Select-String "\.env"
# Should return NOTHING - if you see .env, it's being tracked! ⚠️
```

---

## ✅ That's It!

- ✅ GitHub Secrets: Secure for CI/CD
- ✅ Local .env: Secure for development
- ✅ Not in git: Safe to push code

**Your API key is now secure!** 🔐

For more details, see `SECURITY_GUIDE.md`

