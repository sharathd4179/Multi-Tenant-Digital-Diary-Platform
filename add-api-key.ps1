# PowerShell Script to Securely Add OpenAI API Key
# This script helps you add your API key without exposing it

Write-Host "🔐 Secure API Key Setup" -ForegroundColor Green
Write-Host ""

# Check if .env already exists
if (Test-Path .env) {
    Write-Host "⚠️  .env file already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to update the OPENAI_API_KEY? (y/n)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Get API key securely
Write-Host "Enter your OpenAI API Key (it will be hidden):" -ForegroundColor Cyan
$apiKey = Read-Host -AsSecureString
$apiKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
)

# Validate API key format
if (-not $apiKeyPlain.StartsWith("sk-")) {
    Write-Host "⚠️  Warning: API key should start with 'sk-'" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 0
    }
}

# Create or update .env file
Write-Host ""
Write-Host "📝 Creating/updating .env file..." -ForegroundColor Yellow

$envContent = @"
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/diarydb

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Security
JWT_SECRET_KEY=your_minimum_32_character_secret_key_change_this_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# OpenAI API Key
OPENAI_API_KEY=$apiKeyPlain

# Application
ENVIRONMENT=development
LOG_LEVEL=info
RAG_CHUNK_SIZE=512
RAG_OVERLAP=50
"@

# Write to file
$envContent | Out-File -FilePath .env -Encoding utf8 -NoNewline

# Verify it's ignored by git
Write-Host ""
Write-Host "🔍 Verifying security..." -ForegroundColor Yellow

$isIgnored = git check-ignore .env 2>&1
if ($isIgnored) {
    Write-Host "✅ .env is properly ignored by git" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: .env is NOT ignored by git!" -ForegroundColor Red
    Write-Host "   Please check your .gitignore file" -ForegroundColor Red
}

# Check if .env is tracked
$isTracked = git ls-files .env 2>&1
if ($isTracked) {
    Write-Host "⚠️  WARNING: .env is tracked by git!" -ForegroundColor Red
    Write-Host "   Run: git rm --cached .env" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env is NOT tracked by git" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ API key added to .env file!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Add to GitHub Secrets for CI/CD:" -ForegroundColor White
Write-Host "      https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/settings/secrets/actions" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Verify it's secure:" -ForegroundColor White
Write-Host "      git status  # .env should NOT appear" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. See SECURITY_GUIDE.md for more details" -ForegroundColor White
Write-Host ""

# Clear the plain text key from memory
$apiKeyPlain = $null
[GC]::Collect()

