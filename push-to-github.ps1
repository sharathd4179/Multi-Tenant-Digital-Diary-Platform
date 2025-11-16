# PowerShell Script to Push to GitHub
# Your Repository: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform

Write-Host "🚀 Setting up Git and pushing to GitHub..." -ForegroundColor Green
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    exit 1
}

# Initialize git if not already done
if (-not (Test-Path .git)) {
    Write-Host "📦 Initializing git repository..." -ForegroundColor Yellow
    git init
} else {
    Write-Host "✅ Git repository already initialized" -ForegroundColor Green
}

# Add all files
Write-Host "📝 Adding files..." -ForegroundColor Yellow
git add .

# Check if there are changes to commit
$status = git status --porcelain
if ($status) {
    Write-Host "💾 Committing changes..." -ForegroundColor Yellow
    git commit -m "Initial commit: Multi-tenant diary assistant with CI/CD pipeline"
} else {
    Write-Host "ℹ️  No changes to commit" -ForegroundColor Cyan
}

# Check if remote exists
$remote = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "🔗 Adding GitHub remote..." -ForegroundColor Yellow
    git remote add origin https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git
} else {
    Write-Host "✅ Remote already configured: $remote" -ForegroundColor Green
    Write-Host "🔄 Updating remote URL..." -ForegroundColor Yellow
    git remote set-url origin https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git
}

# Set main branch
Write-Host "🌿 Setting main branch..." -ForegroundColor Yellow
git branch -M main

# Push to GitHub
Write-Host ""
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "   Repository: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform" -ForegroundColor Cyan
Write-Host ""

$pushResult = git push -u origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/settings/secrets/actions" -ForegroundColor Cyan
    Write-Host "   2. Add OPENAI_API_KEY secret" -ForegroundColor Cyan
    Write-Host "   3. Check Actions: https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/actions" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️  Push encountered an issue. Error:" -ForegroundColor Yellow
    Write-Host $pushResult -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 If the repository is not empty, you may need to:" -ForegroundColor Yellow
    Write-Host "   git push -u origin main --force" -ForegroundColor Cyan
    Write-Host "   (Be careful with --force!)" -ForegroundColor Red
}

