# Complete Deployment Script
# This script handles the entire deployment process

Write-Host "🚀 Production Deployment Script" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Step 1: Check Git
Write-Host "📦 Step 1: Checking Git..." -ForegroundColor Yellow
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    exit 1
}

# Initialize git if needed
if (-not (Test-Path .git)) {
    Write-Host "   Initializing git..." -ForegroundColor Cyan
    git init
}

# Step 2: Verify .env is protected
Write-Host ""
Write-Host "🔐 Step 2: Verifying security..." -ForegroundColor Yellow
$isIgnored = git check-ignore .env 2>&1
if ($isIgnored) {
    Write-Host "   ✅ .env is properly ignored" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  WARNING: .env might not be ignored!" -ForegroundColor Red
}

$isTracked = git ls-files .env 2>&1
if ($isTracked -and $LASTEXITCODE -eq 0) {
    Write-Host "   ⚠️  .env is tracked! Removing..." -ForegroundColor Yellow
    git rm --cached .env 2>&1 | Out-Null
}

# Step 3: Add and commit
Write-Host ""
Write-Host "📝 Step 3: Preparing commit..." -ForegroundColor Yellow
git add .

$status = git status --short
if ($status) {
    Write-Host "   Files to commit:" -ForegroundColor Cyan
    git status --short | Select-Object -First 10 | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    
    $commit = Read-Host "   Commit message (or press Enter for default)"
    if ([string]::IsNullOrWhiteSpace($commit)) {
        $commit = "Production-ready: Optimized builds, organized docs, CI/CD pipeline"
    }
    
    git commit -m $commit
    Write-Host "   ✅ Committed" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No changes to commit" -ForegroundColor Cyan
}

# Step 4: Setup remote
Write-Host ""
Write-Host "🔗 Step 4: Setting up GitHub remote..." -ForegroundColor Yellow
$remoteCheck = git remote get-url origin 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Remote exists: $remoteCheck" -ForegroundColor Cyan
    $update = Read-Host "   Update to correct repository? (y/n)"
    if ($update -eq "y" -or $update -eq "Y") {
        git remote set-url origin https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git
        Write-Host "   ✅ Remote updated" -ForegroundColor Green
    }
} else {
    git remote add origin https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git
    Write-Host "   ✅ Remote added" -ForegroundColor Green
}

# Step 5: Push to GitHub
Write-Host ""
Write-Host "🚀 Step 5: Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main

$push = Read-Host "   Push to GitHub now? (y/n)"
if ($push -eq "y" -or $push -eq "Y") {
    Write-Host "   Pushing..." -ForegroundColor Cyan
    $pushResult = git push -u origin main 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Successfully pushed!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Push issue:" -ForegroundColor Yellow
        Write-Host $pushResult -ForegroundColor Red
        
        if ($pushResult -match "not empty" -or $pushResult -match "rejected") {
            $force = Read-Host "   Force push? (overwrites remote) (y/n)"
            if ($force -eq "y" -or $force -eq "Y") {
                git push -u origin main --force
            }
        }
    }
} else {
    Write-Host "   ⏭️  Skipped push" -ForegroundColor Yellow
}

# Step 6: Deployment options
Write-Host ""
Write-Host "🎯 Step 6: Deployment Options" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Choose deployment method:" -ForegroundColor Cyan
Write-Host "   1. GitHub Actions (Automatic) - Tag v1.0.0" -ForegroundColor White
Write-Host "   2. Manual Server Deployment" -ForegroundColor White
Write-Host "   3. Skip for now" -ForegroundColor White
Write-Host ""
$deployChoice = Read-Host "   Your choice (1/2/3)"

switch ($deployChoice) {
    "1" {
        Write-Host ""
        Write-Host "🏷️  Creating version tag..." -ForegroundColor Yellow
        $tag = Read-Host "   Tag version (default: v1.0.0)"
        if ([string]::IsNullOrWhiteSpace($tag)) {
            $tag = "v1.0.0"
        }
        
        git tag $tag
        git push origin $tag
        
        Write-Host ""
        Write-Host "✅ Tag pushed! GitHub Actions will deploy automatically." -ForegroundColor Green
        $actionsUrl = "https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/actions"
        Write-Host "   Monitor: $actionsUrl" -ForegroundColor Cyan
    }
    "2" {
        Write-Host ""
        Write-Host "📋 Manual Deployment Steps:" -ForegroundColor Yellow
        Write-Host "   1. Create .env.production on your server" -ForegroundColor White
        Write-Host "   2. Run: cd infra && docker-compose -f docker-compose.prod.yml up -d" -ForegroundColor White
        Write-Host "   3. Check: docker-compose -f docker-compose.prod.yml ps" -ForegroundColor White
    }
    default {
        Write-Host "   ⏭️  Deployment skipped" -ForegroundColor Yellow
    }
}

# Final summary
Write-Host ""
Write-Host "✅ Deployment Preparation Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Add GitHub Secret (OPENAI_API_KEY):" -ForegroundColor Cyan
$secretsUrl = "https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/settings/secrets/actions"
Write-Host "      $secretsUrl" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Monitor GitHub Actions:" -ForegroundColor Cyan
$actionsUrl2 = "https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/actions"
Write-Host "      $actionsUrl2" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Check Docker Images:" -ForegroundColor Cyan
$packagesUrl = "https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform?tab=packages"
Write-Host "      $packagesUrl" -ForegroundColor Gray
Write-Host ""
