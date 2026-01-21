# Test en mode production (simule Koyeb)
Write-Host "🧪 Test en mode production locale" -ForegroundColor Cyan
Write-Host ""

$projectPath = "c:\Users\Antoine Dupont\Documents\!EFREI\OneDrive - Efrei\!Cours\Projet transverse\Code\Low-Tech-Diploma"
Set-Location $projectPath

# Vérifier que dist/ existe
if (-not (Test-Path "dist")) {
    Write-Host "⚠️  dist/ n'existe pas. Building..." -ForegroundColor Yellow
    npm run build
    Write-Host ""
}

# Vérifier les fichiers essentiels
Write-Host "📋 Vérification des fichiers..." -ForegroundColor Yellow

$essentialFiles = @(
    "dist/index.html",
    "dist/assets",
    "app.py",
    "requirements.txt"
)

$allGood = $true
foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file manquant!" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""

if (-not $allGood) {
    Write-Host "❌ Des fichiers essentiels sont manquants!" -ForegroundColor Red
    exit 1
}

# Vérifier les variables d'environnement
Write-Host "🔐 Vérification des variables d'environnement..." -ForegroundColor Yellow

if (-not $env:JWT_SECRET) {
    Write-Host "  ⚠️  JWT_SECRET non défini - utilisez le .env" -ForegroundColor Yellow
}
if (-not $env:MONGO_URI) {
    Write-Host "  ⚠️  MONGO_URI non défini - utilisez le .env" -ForegroundColor Yellow
}

Write-Host ""

# Simuler le mode production
Write-Host "🚀 Démarrage en mode production..." -ForegroundColor Green
Write-Host ""
Write-Host "Le serveur va démarrer sur http://localhost:5000" -ForegroundColor Cyan
Write-Host "Testez l'application complète (React + Flask)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Yellow
Write-Host ""

# Désactiver le mode debug
$env:FLASK_ENV = "production"

# Lancer Flask
python app.py
