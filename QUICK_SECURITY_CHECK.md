# ✅ Quick Security Check

Run these commands to verify your API key is secure:

## 🔍 Check 1: .env is Ignored

```powershell
git check-ignore .env
```

**Should show:** `.env` ✅

## 🔍 Check 2: .env is NOT Tracked

```powershell
git ls-files | Select-String "\.env"
```

**Should show:** NOTHING ✅

## 🔍 Check 3: .env Not in Git Status

```powershell
git status
```

**Should NOT show:** `.env` ✅

## 🔍 Check 4: No Hardcoded Keys

```powershell
Select-String -Path . -Pattern "sk-[a-zA-Z0-9]{20,}" -Recurse -Exclude "*.md","*.git*","SECURITY_GUIDE.md","ADD_API_KEY.md"
```

**Should show:** NOTHING ✅

---

## ✅ All Checks Pass?

Your API key is secure! 🔐

---

## ⚠️ If Any Check Fails:

1. **If .env is tracked:**
   ```powershell
   git rm --cached .env
   git commit -m "Remove .env from tracking"
   ```

2. **If .env not ignored:**
   - Check `.gitignore` includes `.env`
   - Add it if missing

3. **If hardcoded key found:**
   - Remove it from code
   - Use environment variables instead
   - Rotate the key in OpenAI dashboard

---

## 🎯 Quick Setup

**Use the automated script:**
```powershell
.\add-api-key.ps1
```

Or see `ADD_API_KEY.md` for manual setup.

