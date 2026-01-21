# Checklist de vérification avant de lancer le frontend

Write-Host "🔍 Vérification de l'installation du frontend..." -ForegroundColor Cyan
Write-Host ""

$projectPath = "c:\Users\Antoine Dupont\Documents\!EFREI\OneDrive - Efrei\!Cours\Projet transverse\Code\Low-Tech-Diploma"
$downloadsPath = "c:\Users\Antoine Dupont\Downloads"
$errors = @()
$warnings = @()

# Vérifier les fichiers téléchargés
Write-Host "📥 Vérification des fichiers téléchargés..." -ForegroundColor Yellow
if (Test-Path "$downloadsPath\package.json") {
    Write-Host "  ✅ package.json trouvé" -ForegroundColor Green
} else {
    $errors += "❌ package.json manquant dans Downloads"
}

if (Test-Path "$downloadsPath\src") {
    Write-Host "  ✅ Dossier src trouvé" -ForegroundColor Green
} else {
    $errors += "❌ Dossier src manquant dans Downloads"
}

Write-Host ""

# Vérifier les fichiers créés
Write-Host "📁 Vérification des fichiers du projet..." -ForegroundColor Yellow
$requiredFiles = @(
    "index.html",
    "tsconfig.json",
    "src\main.tsx",
    "src\config.ts",
    "setup-frontend.ps1"
)

foreach ($file in $requiredFiles) {
    if (Test-Path "$projectPath\$file") {
        Write-Host "  ✅ $file créé" -ForegroundColor Green
    } else {
        $warnings += "⚠️  $file n'existe pas encore (sera créé lors du setup)"
    }
}

Write-Host ""

# Vérifier Node.js
Write-Host "🔧 Vérification de Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "  ✅ Node.js installé: $nodeVersion" -ForegroundColor Green
    
    $npmVersion = npm --version
    Write-Host "  ✅ npm installé: $npmVersion" -ForegroundColor Green
} catch {
    $errors += "❌ Node.js n'est pas installé (https://nodejs.org/)"
}

Write-Host ""

# Vérifier Python
Write-Host "🐍 Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "  ✅ Python installé: $pythonVersion" -ForegroundColor Green
} catch {
    $errors += "❌ Python n'est pas installé"
}

Write-Host ""

# Afficher le résumé
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "RÉSUMÉ" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

if ($errors.Count -eq 0) {
    Write-Host "✅ Tout est prêt pour l'installation!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Prochaine étape:" -ForegroundColor Yellow
    Write-Host "   .\setup-frontend.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Des problèmes ont été détectés:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "   $error" -ForegroundColor Red
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "⚠️  Avertissements:" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "   $warning" -ForegroundColor Yellow
    }
    Write-Host ""
}

Write-Host "📚 Pour plus d'informations, consultez:" -ForegroundColor Cyan
Write-Host "   - MIGRATION_GUIDE.md" -ForegroundColor White
Write-Host "   - FRONTEND_SETUP.md" -ForegroundColor White
Write-Host ""
