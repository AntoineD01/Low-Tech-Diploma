# Script d'installation du frontend React généré par Figma
Write-Host "🚀 Installation du Frontend Low-Tech Diploma" -ForegroundColor Cyan
Write-Host ""

$downloadsPath = "c:\Users\Antoine Dupont\Downloads"
$projectPath = "c:\Users\Antoine Dupont\Documents\!EFREI\OneDrive - Efrei\!Cours\Projet transverse\Code\Low-Tech-Diploma"

# Vérifier si les fichiers existent dans Downloads
if (-not (Test-Path "$downloadsPath\package.json")) {
    Write-Host "❌ Erreur: package.json introuvable dans Downloads" -ForegroundColor Red
    Write-Host "Assurez-vous d'avoir téléchargé les fichiers depuis Figma" -ForegroundColor Yellow
    exit 1
}

Write-Host "📁 Copie des fichiers de configuration..." -ForegroundColor Green

# Copier les fichiers de configuration
Copy-Item "$downloadsPath\package.json" $projectPath -Force
Copy-Item "$downloadsPath\vite.config.ts" $projectPath -Force
Copy-Item "$downloadsPath\postcss.config.mjs" $projectPath -Force

Write-Host "✅ Fichiers de configuration copiés" -ForegroundColor Green
Write-Host ""

# Copier le dossier src
Write-Host "📁 Copie du dossier src..." -ForegroundColor Green

# Sauvegarder l'ancien src s'il existe
if (Test-Path "$projectPath\src") {
    Write-Host "⚠️  Un dossier src existe déjà, sauvegarde en src_backup..." -ForegroundColor Yellow
    Remove-Item "$projectPath\src_backup" -Recurse -Force -ErrorAction SilentlyContinue
    Move-Item "$projectPath\src" "$projectPath\src_backup" -Force
}

Copy-Item "$downloadsPath\src" $projectPath -Recurse -Force

Write-Host "✅ Dossier src copié" -ForegroundColor Green
Write-Host ""

# Installation des dépendances
Write-Host "📦 Installation des dépendances Node.js..." -ForegroundColor Green
Write-Host "Cela peut prendre quelques minutes..." -ForegroundColor Yellow
Write-Host ""

Set-Location $projectPath

try {
    npm install
    Write-Host ""
    Write-Host "✅ Dépendances installées avec succès!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de l'installation des dépendances" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Installation terminée avec succès!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "1. Terminal 1 - Backend: python app.py" -ForegroundColor White
Write-Host "2. Terminal 2 - Frontend: npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Le frontend sera disponible sur http://localhost:5173" -ForegroundColor Yellow
Write-Host "Le backend sera disponible sur http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
