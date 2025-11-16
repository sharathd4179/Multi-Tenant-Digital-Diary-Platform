# Complete Setup and Push Script
# This script does everything: init, commit, connect, and push

Write-Host "🚀 Complete Setup and Push to GitHub" -ForegroundColor Green
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    exit 1
}

# Check current directory
Write-Host "📍 Current directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Step 1: Initialize git if needed
if (-not (Test-Path .git)) {
    Write-Host "📦 Initializing git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already initialized" -ForegroundColor Green
}

# Step 2: Verify .env is ignored
Write-Host ""
Write-Host "🔍 Verifying .env is ignored..." -ForegroundColor Yellow
$isIgnored = git check-ignore .env 2>&1
if ($isIgnored) {
    Write-Host "✅ .env is properly ignored by git" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: .env is NOT ignored!" -ForegroundColor Red
    Write-Host "   Checking .gitignore..." -ForegroundColor Yellow
    if (Test-Path .gitignore) {
        $gitignoreContent = Get-Content .gitignore -Raw
        if ($gitignoreContent -match "\.env") {
            Write-Host "   .env is in .gitignore, but git might not see it yet" -ForegroundColor Yellow
        } else {
            Write-Host "   Adding .env to .gitignore..." -ForegroundColor Yellow
            Add-Content .gitignore "`n# Environment files`n.env`n"
        }
    }
}

# Step 3: Check if .env is tracked
Write-Host ""
Write-Host "🔍 Checking if .env is tracked..." -ForegroundColor Yellow
$isTracked = git ls-files .env 2>&1
if ($isTracked -and $LASTEXITCODE -eq 0) {
    Write-Host "⚠️  .env is tracked! Removing from git..." -ForegroundColor Yellow
    git rm --cached .env 2>&1 | Out-Null
    Write-Host "✅ .env removed from tracking" -ForegroundColor Green
} else {
    Write-Host "✅ .env is NOT tracked" -ForegroundColor Green
}

# Step 4: Add all files
Write-Host ""
Write-Host "📝 Adding files to git..." -ForegroundColor Yellow
git add .

# Show what will be committed
Write-Host ""
Write-Host "📋 Files to be committed:" -ForegroundColor Cyan
git status --short | Select-Object -First 20
$totalFiles = (git status --short).Count
Write-Host "   Total: $totalFiles files" -ForegroundColor Gray

# Verify .env is NOT in the list
$envInStatus = git status --short | Select-String "\.env"
if ($envInStatus) {
    Write-Host ""
    Write-Host "⚠️  WARNING: .env appears in git status!" -ForegroundColor Red
    Write-Host "   This should not happen. Please check manually." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
} else {
    Write-Host "✅ .env is NOT in the commit (correct!)" -ForegroundColor Green
}

# Step 5: Commit
Write-Host ""
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
$commitMessage = "Initial commit: Multi-tenant diary assistant with CI/CD pipeline"
git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Committed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  No changes to commit or commit failed" -ForegroundColor Yellow
}

# Step 6: Check remote
Write-Host ""
Write-Host "🔗 Checking remote..." -ForegroundColor Yellow
$remote = git remote get-url origin 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Remote already configured: $remote" -ForegroundColor Green
    $updateRemote = Read-Host "Update to correct repository? (y/n)"
    if ($updateRemote -eq "y" -or $updateRemote -eq "Y") {
        git remote set-url origin https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git
        Write-Host "✅ Remote updated" -ForegroundColor Green
    }
} else {
    Write-Host "📡 Adding GitHub remote..." -ForegroundColor Yellow
    git remote add origin https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git
    Write-Host "✅ Remote added" -ForegroundColor Green
}

# Step 7: Set main branch
Write-Host ""
Write-Host "🌿 Setting main branch..." -ForegroundColor Yellow
git branch -M main
Write-Host "✅ Branch set to main" -ForegroundColor Green

# Step 8: Push to GitHub
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
    Write-Host ""
    Write-Host "1. Add GitHub Secret:" -ForegroundColor Cyan
    Write-Host "   https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/settings/secrets/actions" -ForegroundColor Gray
    Write-Host "   - Name: OPENAI_API_KEY" -ForegroundColor Gray
    Write-Host "   - Value: (from your .env file)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Watch CI/CD Run:" -ForegroundColor Cyan
    Write-Host "   https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/actions" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Verify .env is NOT on GitHub:" -ForegroundColor Cyan
    Write-Host "   Check the repository - .env should NOT be visible" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️  Push encountered an issue:" -ForegroundColor Yellow
    Write-Host $pushResult -ForegroundColor Red
    Write-Host ""
    
    if ($pushResult -match "not empty" -or $pushResult -match "rejected") {
        Write-Host "💡 The repository might not be empty." -ForegroundColor Yellow
        Write-Host "   Options:" -ForegroundColor Yellow
        Write-Host "   1. Force push (overwrites remote):" -ForegroundColor Cyan
        Write-Host "      git push -u origin main --force" -ForegroundColor Gray
        Write-Host "   2. Pull first (merges with remote):" -ForegroundColor Cyan
        Write-Host "      git pull origin main --allow-unrelated-histories" -ForegroundColor Gray
        Write-Host "      git push -u origin main" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green

