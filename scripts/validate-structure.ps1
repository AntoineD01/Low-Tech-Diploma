# Validation de la structure du projet

Write-Host "🔍 VALIDATION DE LA STRUCTURE DU PROJET" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$projectPath = "c:\Users\Antoine Dupont\Documents\!EFREI\OneDrive - Efrei\!Cours\Projet transverse\Code\Low-Tech-Diploma"
Set-Location $projectPath

$allGood = $true

# Vérifier les dossiers
Write-Host "📁 Vérification des dossiers..." -ForegroundColor Yellow
$requiredDirs = @("src", "docs", "scripts", "diplomas", "keys", "templates_old")

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        $count = (Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue).Count
        Write-Host "  ✅ $dir/ ($count fichiers)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $dir/ manquant!" -ForegroundColor Red
        $allGood = $false
    }
}
Write-Host ""

# Vérifier les fichiers essentiels à la racine
Write-Host "📄 Vérification des fichiers essentiels..." -ForegroundColor Yellow
$requiredFiles = @(
    "app.py",
    "package.json",
    "requirements.txt",
    "Procfile",
    "index.html",
    "vite.config.ts",
    "tsconfig.json",
    "README.md",
    ".gitignore"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file manquant!" -ForegroundColor Red
        $allGood = $false
    }
}
Write-Host ""

# Vérifier que les anciens fichiers ont été déplacés
Write-Host "🗑️  Vérification du nettoyage..." -ForegroundColor Yellow
$shouldNotExist = @(
    "templates",
    ".koyeb",
    "package.build.json",
    "MIGRATION_GUIDE.md",
    "FRONTEND_SETUP.md",
    "setup-frontend.ps1",
    "test-production.ps1"
)

$cleanupOk = $true
foreach ($item in $shouldNotExist) {
    if (Test-Path $item) {
        Write-Host "  ⚠️  $item existe encore (devrait être déplacé)" -ForegroundColor Yellow
        $cleanupOk = $false
    }
}

if ($cleanupOk) {
    Write-Host "  ✅ Nettoyage OK - anciens fichiers déplacés" -ForegroundColor Green
}
Write-Host ""

# Vérifier la documentation
Write-Host "📚 Vérification de la documentation..." -ForegroundColor Yellow
$docsFiles = Get-ChildItem "docs" -Filter "*.md" -ErrorAction SilentlyContinue
Write-Host "  ✅ $($docsFiles.Count) fichiers de documentation dans docs/" -ForegroundColor Green
Write-Host ""

# Vérifier les scripts
Write-Host "🔧 Vérification des scripts..." -ForegroundColor Yellow
$scriptsFiles = Get-ChildItem "scripts" -ErrorAction SilentlyContinue
Write-Host "  ✅ $($scriptsFiles.Count) scripts dans scripts/" -ForegroundColor Green
Write-Host ""

# Compter les fichiers à la racine
Write-Host "📊 Statistiques..." -ForegroundColor Yellow
$rootFiles = Get-ChildItem -File | Where-Object { $_.Extension -ne ".txt" }
Write-Host "  📄 Fichiers à la racine: $($rootFiles.Count)" -ForegroundColor Cyan
Write-Host "  📁 Dossiers: $((Get-ChildItem -Directory).Count)" -ForegroundColor Cyan
Write-Host ""

# Résumé
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "RÉSUMÉ" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

if ($allGood) {
    Write-Host "✅ STRUCTURE VALIDÉE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Le projet est correctement organisé:" -ForegroundColor Green
    Write-Host "  • Documentation dans docs/" -ForegroundColor White
    Write-Host "  • Scripts dans scripts/" -ForegroundColor White
    Write-Host "  • Anciens templates dans templates_old/" -ForegroundColor White
    Write-Host "  • Fichiers essentiels à la racine" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Prêt pour le développement et le déploiement!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Des éléments manquent" -ForegroundColor Yellow
    Write-Host "Consultez les erreurs ci-dessus" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📖 Documentation: docs/PROJECT_STRUCTURE.md" -ForegroundColor Cyan
Write-Host "📋 Résumé nettoyage: docs/CLEANUP_SUMMARY.md" -ForegroundColor Cyan
Write-Host ""
