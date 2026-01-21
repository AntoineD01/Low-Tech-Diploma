# Checklist de déploiement Koyeb

Write-Host "✅ CHECKLIST DÉPLOIEMENT KOYEB" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$projectPath = "c:\Users\Antoine Dupont\Documents\!EFREI\OneDrive - Efrei\!Cours\Projet transverse\Code\Low-Tech-Diploma"
Set-Location $projectPath

$checks = @()

# 1. Fichiers essentiels
Write-Host "📁 1. Fichiers essentiels" -ForegroundColor Yellow
$requiredFiles = @{
    "package.json" = "Configuration Node.js"
    "vite.config.ts" = "Configuration Vite"
    "requirements.txt" = "Dépendances Python"
    "Procfile" = "Configuration Koyeb"
    "app.py" = "Application Flask"
    "src/main.tsx" = "Point d'entrée React"
}

foreach ($file in $requiredFiles.Keys) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file - $($requiredFiles[$file])" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host "  ❌ $file manquant!" -ForegroundColor Red
        $checks += $false
    }
}
Write-Host ""

# 2. Build local
Write-Host "🏗️  2. Build local" -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "  ✅ node_modules installé" -ForegroundColor Green
    $checks += $true
} else {
    Write-Host "  ⚠️  node_modules manquant - exécutez 'npm install'" -ForegroundColor Yellow
    $checks += $false
}

if (Test-Path "dist") {
    $distFiles = Get-ChildItem "dist" -Recurse
    if ($distFiles.Count -gt 0) {
        Write-Host "  ✅ dist/ généré ($($distFiles.Count) fichiers)" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host "  ❌ dist/ vide - exécutez 'npm run build'" -ForegroundColor Red
        $checks += $false
    }
} else {
    Write-Host "  ⚠️  dist/ manquant - exécutez 'npm run build'" -ForegroundColor Yellow
    $checks += $false
}
Write-Host ""

# 3. Git
Write-Host "📦 3. Git" -ForegroundColor Yellow
try {
    $gitStatus = git status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Repository Git initialisé" -ForegroundColor Green
        $checks += $true
        
        # Vérifier s'il y a des modifications non committées
        $hasChanges = git status --porcelain
        if ($hasChanges) {
            Write-Host "  ⚠️  Modifications non committées détectées" -ForegroundColor Yellow
            Write-Host "     Exécutez: git add . && git commit -m 'Update'" -ForegroundColor White
        } else {
            Write-Host "  ✅ Pas de modifications non committées" -ForegroundColor Green
        }
        
        # Vérifier la branche
        $branch = git branch --show-current
        Write-Host "  📍 Branche actuelle: $branch" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ⚠️  Git non initialisé" -ForegroundColor Yellow
    $checks += $false
}
Write-Host ""

# 4. Variables d'environnement
Write-Host "🔐 4. Variables d'environnement (à configurer dans Koyeb)" -ForegroundColor Yellow
$envVars = @{
    "JWT_SECRET" = "Secret pour JWT"
    "MONGO_URI" = "URI MongoDB Atlas"
    "ALLOWED_ORIGIN" = "URL de votre app Koyeb"
}

Write-Host "  Variables requises dans Koyeb Dashboard:" -ForegroundColor Cyan
foreach ($var in $envVars.Keys) {
    Write-Host "  • $var - $($envVars[$var])" -ForegroundColor White
}
Write-Host ""

# 5. Test local en mode production
Write-Host "🧪 5. Test local" -ForegroundColor Yellow
Write-Host "  Pour tester avant déploiement:" -ForegroundColor Cyan
Write-Host "  → .\test-production.ps1" -ForegroundColor White
Write-Host ""

# Résumé
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "RÉSUMÉ" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$successCount = ($checks | Where-Object { $_ -eq $true }).Count
$totalCount = $checks.Count

if ($successCount -eq $totalCount) {
    Write-Host "✅ PRÊT POUR DÉPLOIEMENT! ($successCount/$totalCount checks passés)" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Prochaines étapes:" -ForegroundColor Cyan
    Write-Host "1. git add . && git commit -m 'Add React frontend'" -ForegroundColor White
    Write-Host "2. git push origin main" -ForegroundColor White
    Write-Host "3. Configurer les variables d'environnement dans Koyeb" -ForegroundColor White
    Write-Host "4. Déployer depuis le Dashboard Koyeb" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Documentation: KOYEB_QUICKSTART.md" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Quelques vérifications ont échoué ($successCount/$totalCount)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Corrigez les problèmes ci-dessus avant de déployer" -ForegroundColor Yellow
}
Write-Host ""
