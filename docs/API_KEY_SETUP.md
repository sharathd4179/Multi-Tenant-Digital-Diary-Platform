# 🔑 API Key Setup

## Quick Setup (2 Minutes)

### 1. Add to GitHub Secrets

1. Go to: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/settings/secrets/actions
2. Click "New repository secret"
3. Name: `OPENAI_API_KEY`
4. Value: Your OpenAI API key
5. Click "Add secret"

### 2. Add to Local .env

Create `.env` file:

```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Verify Security

```bash
git check-ignore .env  # Should show: .env
git status  # .env should NOT appear
```

## Automated Setup

Run the setup script:

```powershell
.\add-api-key.ps1
```

## Get Your API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign in/up
3. Create new API key
4. Copy the key (starts with `sk-`)

## Troubleshooting

- **Key not working?** Check it's correct in `.env` and GitHub Secrets
- **Key exposed?** Rotate it immediately in OpenAI dashboard
- **Not ignored?** Check `.gitignore` includes `.env`

See [Security Guide](SECURITY.md) for more details.

