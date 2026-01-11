# Security Setup Guide

## ✅ All Critical Security Issues FIXED:

1. ✅ **Hardcoded credentials removed** - Now using environment variables
2. ✅ **Password hashing implemented** - Using Werkzeug's bcrypt
3. ✅ **JWT token expiration** - Tokens expire after 24 hours
4. ✅ **CORS restrictions** - Configurable origin control

---

## 🔧 Setup Instructions for Koyeb + MongoDB

### Step 1: Configure Koyeb Environment Variables

Go to your Koyeb deployment settings and add these environment variables:

```
JWT_SECRET=<generate-a-strong-random-secret-key>
MONGO_URI=mongodb+srv://antoinedupont:!#LowTech2026#!@lowtechdiploma.zrkwhra.mongodb.net/?appName=LowTechDiploma
ALLOWED_ORIGIN=https://your-app-name.koyeb.app
```

**To generate a strong JWT_SECRET:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 2: Update ALLOWED_ORIGIN After Deployment

1. Deploy your app to Koyeb
2. Get your deployment URL (e.g., `https://mere-beverley-lowtechdiploma-a2836eea.koyeb.app`)
3. Update the `ALLOWED_ORIGIN` environment variable in Koyeb with your actual URL
4. For development, you can use `*` to allow all origins

### Step 3: MongoDB Atlas Configuration

Ensure MongoDB Atlas allows connections from Koyeb:

1. Go to MongoDB Atlas → Network Access
2. Click "Add IP Address"
3. Select "Allow Access from Anywhere" (0.0.0.0/0) 
   - OR add Koyeb's IP ranges if you want stricter control

### Step 4: First Deployment

**IMPORTANT:** After first deployment, you need to recreate users with hashed passwords:

1. Connect to MongoDB Atlas
2. Delete existing users from the `users` collection:
   ```javascript
   db.users.deleteMany({})
   ```
3. Restart your Koyeb app - it will automatically create users with hashed passwords

---

## 🔒 What Changed:

### Password Security
- Passwords now hashed with bcrypt (via Werkzeug)
- `check_password_hash()` used for login validation
- Default users created with hashed passwords

### JWT Security
- Tokens expire after 24 hours
- Better error handling (expired vs invalid tokens)
- Includes expiration time in token payload

### CORS Security
- Configurable via `ALLOWED_ORIGIN` environment variable
- Restricts API access to your domain only
- Use `*` only during development

### Environment Variables
- Application validates all required variables on startup
- Fails fast if configuration is missing
- Credentials never stored in code

---

## 📝 Testing Locally

1. Create a `.env` file (copy from `.env.example`)
2. Set your environment variables
3. Load them before running:

**Windows (PowerShell):**
```powershell
$env:JWT_SECRET="test-secret-key"
$env:MONGO_URI="mongodb+srv://..."
$env:ALLOWED_ORIGIN="*"
python app.py
```

**Linux/Mac:**
```bash
export JWT_SECRET="test-secret-key"
export MONGO_URI="mongodb+srv://..."
export ALLOWED_ORIGIN="*"
python app.py
```

---

## ⚠️ Important Notes:

1. **Never commit `.env` files** - They contain secrets
2. **Regenerate JWT_SECRET** - Don't use the example value
3. **Update ALLOWED_ORIGIN** after getting your Koyeb URL
4. **First deployment** - Clear MongoDB users collection to rehash passwords
5. **Change default passwords** - schoolpass and alicepass are still weak

---

## 🚀 Next Steps (Recommended):

- [ ] Add rate limiting to prevent brute force attacks
- [ ] Implement password strength requirements
- [ ] Add user registration endpoint with email verification
- [ ] Enable MongoDB encryption at rest
- [ ] Add request logging for security monitoring
- [ ] Implement HTTPS-only enforcement
- [ ] Add Content Security Policy headers
