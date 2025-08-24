# File: CREDENTIAL_MANAGEMENT.md
# Path: /home/herb/Desktop/AndyLibrary/CREDENTIAL_MANAGEMENT.md
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 08:40PM

# CREDENTIAL MANAGEMENT BEST PRACTICES FOR PROJECT HIMALAYA

## 🔐 ENVIRONMENT VARIABLE APPROACH (RECOMMENDED)

### **1. Local Development Setup**

```bash
# Copy template to real environment file
cp .env.template .env

# Edit .env with your real credentials
nano .env
```

**Your .env file** (never committed to git):
```bash
# Google OAuth Credentials
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
GOOGLE_API_KEY=YOUR_API_KEY_HERE
GOOGLE_PROJECT_ID=andygoogle-project

# Application Settings
APP_SECRET_KEY=super-secret-key-for-production
DEBUG=true
ENVIRONMENT=development
```

### **2. Production Deployment**

**Option A: Cloud Environment Variables**
```bash
# Heroku
heroku config:set GOOGLE_CLIENT_ID=your-real-id

# AWS Lambda
aws lambda update-function-configuration --function-name andylibrary \
  --environment Variables='{GOOGLE_CLIENT_ID=your-real-id}'

# Google Cloud Run
gcloud run services update andylibrary \
  --set-env-vars GOOGLE_CLIENT_ID=your-real-id
```

**Option B: Container Secrets**
```dockerfile
# Docker with secrets
docker run -e GOOGLE_CLIENT_ID=your-real-id andylibrary

# Docker Compose with .env
# (docker-compose.yml automatically loads .env file)
```

**Option C: Cloud Secret Managers**
```python
# AWS Secrets Manager
import boto3
secrets = boto3.client('secretsmanager')
secret = secrets.get_secret_value(SecretId='andylibrary/google-creds')

# Google Secret Manager
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
secret = client.access_secret_version(request={"name": "projects/PROJECT/secrets/google-creds/versions/latest"})
```

## 🔧 USING THE ENVIRONMENT CONFIG

### **In Your Code**

```python
# Simple usage
from Source.Utils.EnvironmentConfig import GetGoogleCredentials, GetServerConfig

# Get Google credentials
creds = GetGoogleCredentials()
client_id = creds['client_id']
client_secret = creds['client_secret']

# Get server settings
server = GetServerConfig()
host = server['host']
port = server['port']
```

### **Advanced Usage**

```python
from Source.Utils.EnvironmentConfig import EnvironmentConfig

# Custom config with different .env file
config = EnvironmentConfig('.env.production')

# Validate configuration
validation = config.ValidateConfiguration()
if validation['errors']:
    print("❌ Configuration errors:", validation['errors'])
    exit(1)

if validation['warnings']:
    print("⚠️ Configuration warnings:", validation['warnings'])

# Use configuration
if config.IsProduction():
    # Production-specific setup
    pass
else:
    # Development setup
    pass
```

## 🛡️ SECURITY HIERARCHY (BEST TO WORST)

### **1. 🥇 Cloud Secret Managers** (Production)
- AWS Secrets Manager, Google Secret Manager, Azure Key Vault
- Automatic rotation, audit logs, fine-grained access
- **Best for**: Production deployments

### **2. 🥈 Environment Variables** (Most Common)
- Set at runtime, not stored in code
- Platform-specific (Heroku config, Docker env, etc.)
- **Best for**: Development and simple production

### **3. 🥉 .env Files** (Development Only)
- Local files excluded from git
- Easy for development, manual for production
- **Best for**: Local development only

### **4. ❌ Hardcoded** (Never Do This)
- Credentials directly in source code
- **Security risk**: Exposed in git history, logs, etc.
- **Never do this**: We already cleaned this up!

## 📋 SETUP CHECKLIST

### **For New Developers**

```bash
# 1. Clone repository
git clone https://github.com/CallMeChewy/AndyLibrary.git
cd AndyLibrary

# 2. Copy environment template
cp .env.template .env

# 3. Get Google Cloud Console credentials
# - Go to console.cloud.google.com
# - Create project or select existing
# - Enable Google Drive API
# - Create OAuth 2.0 credentials
# - Download credentials JSON

# 4. Update .env file with real values
nano .env

# 5. Install dependencies
pip install -r requirements.txt

# 6. Install python-dotenv for automatic .env loading
pip install python-dotenv

# 7. Run application
python StartAndyGoogle.py
```

### **For Production Deployment**

```bash
# 1. Never use .env files in production
# 2. Set environment variables at platform level
# 3. Use secure secret management
# 4. Enable audit logging
# 5. Rotate credentials regularly
```

## 🔍 VALIDATION AND TESTING

### **Check Configuration Status**

```python
from Source.Utils.EnvironmentConfig import ValidateConfiguration

validation = ValidateConfiguration()
print("Google Credentials:", "✅" if validation['google_credentials'] else "❌")
print("Warnings:", validation['warnings'])
print("Errors:", validation['errors'])
```

### **Test Environment Loading**

```bash
# Test with .env file
python -c "from Source.Utils.EnvironmentConfig import GetGoogleCredentials; print(GetGoogleCredentials())"

# Test with environment variables
GOOGLE_CLIENT_ID=test-id python -c "from Source.Utils.EnvironmentConfig import GetGoogleCredentials; print(GetGoogleCredentials())"
```

## 🚀 DEPLOYMENT EXAMPLES

### **Heroku Deployment**

```bash
# Set environment variables
heroku config:set GOOGLE_CLIENT_ID=your-real-client-id
heroku config:set GOOGLE_CLIENT_SECRET=your-real-secret
heroku config:set ENVIRONMENT=production

# Deploy
git push heroku main
```

### **Docker Deployment**

```dockerfile
# Dockerfile
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "StartAndyGoogle.py"]
```

```bash
# Build and run with environment variables
docker build -t andylibrary .
docker run -e GOOGLE_CLIENT_ID=your-real-id andylibrary
```

### **Google Cloud Run**

```bash
# Deploy with secrets
gcloud run deploy andylibrary \
  --source . \
  --set-env-vars ENVIRONMENT=production \
  --set-env-vars GOOGLE_CLIENT_ID=your-real-id \
  --allow-unauthenticated
```

## 📚 ADDITIONAL SECURITY MEASURES

### **1. Credential Rotation**
- Change credentials quarterly
- Use different credentials for dev/staging/production
- Monitor for unauthorized access

### **2. Access Control**
- Limit who can access production credentials
- Use separate Google Cloud projects for environments
- Enable audit logging

### **3. Monitoring**
- Monitor for credential usage patterns
- Set up alerts for unusual API usage
- Regular security audits

## 🎯 PROJECT HIMALAYA SPECIFIC NOTES

### **Google Drive Integration**
- Requires OAuth 2.0 credentials for user authentication
- API key for read-only operations
- Scopes limited to read-only for security

### **Student Protection**
- Budget settings configurable via environment
- Regional pricing adjustable for different deployments
- Cost thresholds tunable for different user bases

### **Educational Mission**
- Credentials support the mission of educational access
- Security measures protect student data and usage
- Transparent cost controls serve the educational community

---

**Remember**: Good credential management is not just about security—it's about enabling the educational mission while protecting students and the platform. Every security decision should serve the goal of getting education into the hands of those who need it most.

**PROJECT HIMALAYA: Where security serves education, not the reverse.** 🏔️🔐