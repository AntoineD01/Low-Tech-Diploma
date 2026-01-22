# Low-Tech Diploma Platform

Système sécurisé de gestion de diplômes numériques avec signatures cryptographiques Ed25519, interface React moderne et déploiement sur Koyeb.

## ✨ Fonctionnalités

### 🎓 Pour les Écoles
- **Émission individuelle** de diplômes avec signature cryptographique
- **Import en masse** via fichiers CSV/Excel pour émettre plusieurs diplômes simultanément
- **Génération automatique** de comptes étudiants avec mots de passe sécurisés
- **Export PDF** de chaque diplôme avec QR code de vérification
- **Envoi d'emails** automatique aux étudiants avec leurs identifiants et diplôme
- **Révocation** de diplômes si nécessaire
- **Tableau de bord** pour visualiser tous les diplômes émis

### 👨‍🎓 Pour les Étudiants
- **Consultation** de leurs diplômes avec détails complets
- **Téléchargement** en format JSON (blockchain-ready) et PDF
- **Partage** sécurisé via liens de vérification

### 🔒 Pour Tous
- **Vérification publique** de l'authenticité des diplômes
- **Signatures cryptographiques** Ed25519 infalsifiables
- **Stockage sécurisé** dans MongoDB Atlas

## 🏗️ Structure du Projet

```
Low-Tech-Diploma/
├── src/                    # Frontend React + TypeScript
│   ├── app/
│   │   ├── components/     # Composants UI (shadcn/ui)
│   │   ├── contexts/       # AuthContext, DiplomaContext
│   │   └── pages/          # Pages de l'application
│   └── styles/             # CSS et thèmes
├── app.py                  # Backend Flask avec API REST
├── diplomas/               # Stockage local des diplômes (backup)
├── pdfs/                   # PDFs générés
├── keys/                   # Clés cryptographiques (gitignored)
├── scripts/                # Scripts PowerShell de setup et test
└── dist/                   # Build de production (généré)
```

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.11+
- Node.js 18+
- MongoDB Atlas (ou instance locale)

### Installation

```powershell
# 1. Installer les dépendances frontend
.\scripts\setup-frontend.ps1

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations
```

### Développement Local

```powershell
# Terminal 1 - Backend Flask (port 5000)
python app.py

# Terminal 2 - Frontend Vite (port 5173 avec proxy)
npm run dev
```

### Build de Production

```powershell
# Build le frontend dans dist/
npm run build

# Lance le serveur complet
python app.py
```

## 🌐 Déploiement Koyeb

### Vérification avant déploiement
```powershell
.\scripts\check-koyeb-ready.ps1
```

### Déploiement
```powershell
git add .
git commit -m "Deploy: Description des changements"
git push origin main
```

Koyeb détecte automatiquement les changements et redéploie l'application.

### Variables d'environnement Koyeb requises
- `JWT_SECRET` - Secret pour les tokens JWT
- `MONGO_URI` - URI de connexion MongoDB Atlas
- `ALLOWED_ORIGIN` - URL de votre app Koyeb (ou `*` en dev)
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` - Configuration email (optionnel)

## 📦 Import en Masse

### Format du fichier CSV/Excel

Le fichier doit contenir ces colonnes obligatoires :

| student_name | student_email | degree_name |
|--------------|---------------|-------------|
| Jean Dupont | jean.dupont@example.com | Master en Informatique |
| Marie Martin | marie.martin@example.com | Licence en Mathématiques |

### Utilisation

1. Connectez-vous en tant qu'école
2. Allez dans **"Émettre un Diplôme"**
3. Cliquez sur l'onglet **"Import en masse"**
4. Téléchargez le modèle CSV (optionnel)
5. Uploadez votre fichier
6. Consultez les résultats détaillés

Le système crée automatiquement :
- ✅ Comptes étudiants avec mots de passe générés
- ✅ Diplômes signés cryptographiquement
- ✅ PDFs avec QR codes
- ✅ Emails avec identifiants et diplômes

## 🔐 Sécurité

- **Signatures Ed25519** : Chaque diplôme est signé avec une clé privée unique
- **JWT Tokens** : Authentification sécurisée avec expiration 24h
- **Mots de passe hashés** : Utilisation de Werkzeug pour le hashing
- **CORS configuré** : Protection contre les requêtes non autorisées
- **Validation des rôles** : Endpoints protégés par rôle (school/student)

## 🛠️ Technologies

### Frontend
- **React 18** avec TypeScript
- **React Router** pour le routing SPA
- **Tailwind CSS** pour le styling
- **shadcn/ui** pour les composants UI
- **Vite** comme bundler

### Backend
- **Flask** pour l'API REST
- **MongoDB** avec PyMongo pour la base de données
- **cryptography** pour les signatures Ed25519
- **PyJWT** pour l'authentification
- **ReportLab** pour la génération de PDF
- **Flask-Mail** pour l'envoi d'emails
- **pandas** pour l'import en masse (CSV/Excel)

## 🔍 Debugging

### Logs détaillés
L'application inclut un système de logging complet :
- Chaque requête est loguée avec méthode, path, et endpoint
- Les erreurs 404 et 500 incluent des détails de débogage
- Utilisez `/debug/routes` pour voir toutes les routes enregistrées
- Utilisez `/api/health` pour vérifier l'état du backend

### Problèmes courants

**404 sur les pages après reload**
- ✅ Résolu : Flask sert `index.html` pour toutes les routes GET
- Le SPA routing est géré côté client par React Router

**Erreur "Invalid token"**
- ✅ Vérifié : Le backend supporte le format `Bearer token`
- Vérifiez que JWT_SECRET est identique en dev et prod

**Import en masse échoue**
- Vérifiez que pandas est installé : `pip install pandas openpyxl`
- Vérifiez le format du fichier CSV/Excel
- Consultez les logs Koyeb pour les erreurs détaillées

## 📚 Documentation Complète

- [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) - Migration HTML → React
- [docs/FRONTEND_SETUP.md](docs/FRONTEND_SETUP.md) - Configuration frontend
- [docs/KOYEB_QUICKSTART.md](docs/KOYEB_QUICKSTART.md) - Déploiement Koyeb

## 👥 Comptes par Défaut

### Compte École
- **Username:** `school`
- **Password:** `schoolpass`

### Compte Étudiant (exemple)
- **Username:** `alice`
- **Password:** `alicepass`

*Note: Changez ces mots de passe en production !*

## 📝 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou un pull request.

---

**Développé pour EFREI Paris** - Projet Transverse 2026
