# SecureAuth System Setup for Windows PowerShell

Write-Host "🔐 SecureAuth System Setup" -ForegroundColor Cyan
Write-Host "============================`n" -ForegroundColor Cyan

# Step 1: Create virtual environment
Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -eq 0) { Write-Host "✓ Virtual environment created" -ForegroundColor Green }
else { Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red; exit 1 }

# Step 2: Activate virtual environment
Write-Host "`nStep 2: Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Step 3: Upgrade pip
Write-Host "`nStep 3: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ pip upgraded" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to upgrade pip" -ForegroundColor Red
    exit 1
}

# Step 4: Install dependencies
Write-Host "`nStep 4: Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 5: Create .env file
Write-Host "`nStep 5: Creating .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠ .env already exists, skipping..." -ForegroundColor Yellow
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created from .env.example" -ForegroundColor Green
    Write-Host "⚠ IMPORTANT: Edit .env with your Supabase and SMTP credentials!" -ForegroundColor Yellow
}

# Step 6: Summary
Write-Host "`n✅ Setup Complete!" -ForegroundColor Green
Write-Host "============================`n" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your Supabase URL, API key, and SMTP credentials" -ForegroundColor White
Write-Host "2. Create the users table in Supabase (see DEPLOYMENT_GUIDE.md)" -ForegroundColor White
Write-Host "3. Run: python app.py" -ForegroundColor White
Write-Host "4. Visit: http://localhost:5000" -ForegroundColor White
Write-Host "`n"
