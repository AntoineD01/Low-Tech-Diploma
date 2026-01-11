# Low-Tech Diploma Platform

A secure, decentralized diploma issuance and verification system using cryptographic signatures and MongoDB.

## 🎓 Features

### Core Functionality
- **Digital Diploma Issuance**: Schools can issue cryptographically signed diplomas
- **Diploma Verification**: Anyone can verify the authenticity of a diploma using Ed25519 signatures
- **Diploma Management**: Students can view and download their diplomas
- **Revocation System**: Schools can revoke diplomas if needed

### Security Features
- **Password Hashing**: Bcrypt-based password hashing for user accounts
- **JWT Authentication**: Secure token-based authentication with 24-hour expiration
- **Ed25519 Signatures**: Cryptographic signing for diploma authenticity
- **CORS Protection**: Configurable origin restrictions
- **Environment Variables**: Secure configuration management

### Automation
- **Auto Account Creation**: Student accounts created automatically when diplomas are issued
- **Auto Password Generation**: Secure random passwords (12 characters with letters, digits, symbols)
- **Email Notifications**: Automated emails sent to students with login credentials and diploma information
- **Key Auto-Generation**: Cryptographic keys generated automatically on first run

## 🏗️ Architecture

### Tech Stack
- **Backend**: Flask 3.0.0
- **Database**: MongoDB Atlas
- **Authentication**: JWT + Werkzeug password hashing
- **Cryptography**: Ed25519 (cryptography library)
- **Email**: Flask-Mail
- **Deployment**: Koyeb (production), Gunicorn WSGI server

### Database Collections
- **users**: User accounts (school, students) with hashed passwords
- **diplomas**: Issued diplomas with cryptographic signatures

## 📋 Prerequisites

- Python 3.11+
- MongoDB Atlas account
- Email account for sending notifications (Gmail recommended)
- Koyeb account (for deployment)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Low-Tech-Diploma
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file or set environment variables:

```env
# Required
JWT_SECRET=your-secret-key-here
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=AppName

# Optional (for production)
ALLOWED_ORIGIN=https://your-domain.koyeb.app

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your.email@gmail.com
```

### 4. Run the Application

**Development:**
```bash
python app.py
```

**Production (Koyeb):**
The app will be started automatically using the Procfile configuration:
```
web: gunicorn app:app
```

## 📧 Email Setup (Gmail)

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Create a password for "Mail"
   - Use this password for `MAIL_PASSWORD`

## 🌐 Deployment on Koyeb

### Environment Variables to Set:
```
JWT_SECRET=<random-secret-key>
MONGO_URI=mongodb+srv://...
ALLOWED_ORIGIN=https://<your-app>.koyeb.app
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=<gmail-app-password>
```

### MongoDB Atlas Setup:
1. Create a cluster on MongoDB Atlas
2. Set Network Access to `0.0.0.0/0` (allow from anywhere)
3. Create database: `lowtechdiploma`
4. Collections will be created automatically

### First Deployment:
1. Push code to GitHub
2. Connect repository to Koyeb
3. Set environment variables
4. Deploy
5. Default users will be created automatically:
   - `school` / `schoolpass` (admin)
   - `alice` / `alicepass` (student)

## 👥 Default Users

On first run, two default users are created:

| Username | Password    | Role    |
|----------|-------------|---------|
| school   | schoolpass  | school  |
| alice    | alicepass   | student |

**⚠️ Important**: Change these passwords in production!

## 📖 Usage

### For Schools

1. **Login**: Access `/login.html` with school credentials
2. **Issue Diploma**:
   - Navigate to "Émettre" (Issue)
   - Enter student name (will be username)
   - Enter student email
   - Enter diploma name
   - Click "Émettre"
   - System will:
     - Create student account with auto-generated password
     - Issue cryptographically signed diploma
     - Send email to student with credentials
3. **View All Diplomas**: Access "Tous les diplômes"
4. **Revoke Diplomas**: Use the revoke form on the issue page

### For Students

1. **Check Email**: Receive credentials via email when diploma is issued
2. **Login**: Use provided username and password
3. **View Diplomas**: Access "Mes diplômes" to see your diplomas
4. **Download**: Download diploma as JSON file
5. **Verify**: Anyone can verify the diploma using the downloaded file

### For Public Verification

1. Go to "Vérifier" (Verify) page
2. Upload diploma JSON file or paste content
3. System verifies:
   - Diploma exists in database
   - Not revoked
   - Cryptographic signature is valid

## 🔐 Security Best Practices

1. **Always use strong secrets** for `JWT_SECRET`
2. **Never commit** `.env` files or secrets to git
3. **Change default passwords** immediately after deployment
4. **Use HTTPS** in production (Koyeb provides this)
5. **Restrict CORS** with `ALLOWED_ORIGIN` in production
6. **Rotate keys** periodically
7. **Monitor MongoDB access logs**

## 📁 Project Structure

```
Low-Tech-Diploma/
├── app.py                 # Main Flask application
├── generate_keys.py       # Manual key generation script
├── requirements.txt       # Python dependencies
├── Procfile              # Koyeb deployment config
├── README.md             # This file
├── keys/                 # Cryptographic keys (auto-generated)
│   ├── private_key.pem
│   └── public_key.pem
├── diplomas/             # Legacy directory (kept for compatibility)
├── static/               # Static assets
└── templates/            # HTML templates
    ├── index.html        # Home page
    ├── login.html        # Login page
    ├── issue.html        # Diploma issuance (school only)
    ├── verify.html       # Public verification
    ├── my_diplomas.html  # Student diplomas view
    └── all_diplomas.html # All diplomas view (school only)
```

## 🔄 API Endpoints

### Authentication
- `POST /login` - User login (returns JWT token)

### Diplomas
- `POST /issue` - Issue new diploma (school only)
- `POST /verify` - Verify diploma signature
- `POST /revoke` - Revoke diploma (school only)
- `GET /diploma/<id>` - Get diploma details (authenticated)
- `GET /list` - List all diplomas (authenticated)
- `GET /download/<id>` - Download diploma JSON

### Pages
- `GET /` or `/index.html` - Home page
- `GET /login.html` - Login page
- `GET /issue.html` - Issue diploma page
- `GET /verify.html` - Verify diploma page
- `GET /my_diplomas.html` - Student diplomas
- `GET /all_diplomas.html` - All diplomas (school)

## 🛠️ Troubleshooting

### MongoDB Connection Issues
- Verify `MONGO_URI` is correct
- Check Network Access in MongoDB Atlas (should include `0.0.0.0/0`)
- Ensure database user has read/write permissions

### Email Not Sending
- Verify Gmail App Password is correct
- Check `MAIL_USERNAME` and `MAIL_PASSWORD` are set
- Ensure 2FA is enabled on Gmail account
- Check Koyeb logs for email errors

### Login Fails (401 Error)
- Delete all users in MongoDB users collection
- Redeploy app to recreate users with hashed passwords
- Or check password hash format in database

### Keys Missing
- Keys auto-generate on first run
- Check `keys/` directory exists
- Verify write permissions

## 📝 License

[Your License Here]

## 👨‍💻 Contributing

[Contributing guidelines if applicable]

## 📞 Support

For issues or questions, please [create an issue/contact method]