# Build script for production deployment

Write-Host "🏗️  Building Low-Tech Diploma for production..." -ForegroundColor Cyan
Write-Host ""

$projectPath = "c:\Users\Antoine Dupont\Documents\!EFREI\OneDrive - Efrei\!Cours\Projet transverse\Code\Low-Tech-Diploma"
Set-Location $projectPath

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies first..." -ForegroundColor Yellow
    npm install
    Write-Host ""
}

# Build the frontend
Write-Host "🔨 Building React frontend..." -ForegroundColor Green
try {
    npm run build
    Write-Host ""
    Write-Host "✅ Frontend built successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 Build output in: dist/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🚀 You can now deploy or run:" -ForegroundColor Yellow
    Write-Host "   python app.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Flask will serve the built React app from the dist/ folder" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
