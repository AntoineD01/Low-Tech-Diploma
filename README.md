# Low-Tech Diploma Platform

Système sécurisé de gestion de diplômes avec signatures cryptographiques et interface React moderne.

##  Structure du Projet

- **src/** - Code source React (frontend)
- **app.py** - Application Flask (backend)
- **docs/** - Documentation complète
- **scripts/** - Scripts d'installation et tests
- **diplomas/** - Diplômes émis
- **templates_old/** - Anciens templates HTML (backup)

##  Démarrage Rapide

### Installation
```powershell
.\scripts\setup-frontend.ps1
```

### Développement
```powershell
# Terminal 1 - Backend
python app.py

# Terminal 2 - Frontend
npm run dev
```

##  Déploiement Koyeb

```powershell
.\scripts\check-koyeb-ready.ps1
git push origin main
```

 **Guide complet:** [docs/KOYEB_QUICKSTART.md](docs/KOYEB_QUICKSTART.md)

##  Documentation

- [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)
- [docs/FRONTEND_SETUP.md](docs/FRONTEND_SETUP.md)
- [docs/KOYEB_QUICKSTART.md](docs/KOYEB_QUICKSTART.md)
