# 🚀 Deployment & Security Guide

## Quick Start for Development

### 1. Install Python 3.9+
```bash
python --version  # Should be 3.9 or higher
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Supabase Database

Go to https://supabase.com and create a new project:

```sql
-- Create users table
CREATE TABLE users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    username VARCHAR(32) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(32) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token_hash VARCHAR(64),
    verification_token_expires TIMESTAMP,
    password_reset_token_hash VARCHAR(64),
    password_reset_token_expires TIMESTAMP,
    failed_login_attempts INT DEFAULT 0,
    account_locked_until TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_verification_token ON users(verification_token_hash);
CREATE INDEX idx_users_reset_token ON users(password_reset_token_hash);
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
FLASK_ENV=development
FLASK_DEBUG=False
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=<from Supabase Settings > API >anon key>
SUPABASE_SERVICE_ROLE_KEY=<from Supabase Settings > API > service_role key>
PEPPER=<generate: python -c "import secrets; print(secrets.token_hex(32))">
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=<Gmail app password>
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=SecureAuth
```

### 6. Generate Secure Keys

```python
import secrets
print("SECRET_KEY:", secrets.token_hex(32))
print("PEPPER:", secrets.token_hex(32))
```

### 7. Run Application

```bash
python app.py
```

Visit http://localhost:5000

---

## Production Deployment

### Using Heroku

```bash
# 1. Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login to Heroku
heroku login

# 3. Create app
heroku create your-app-name

# 4. Add environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set PEPPER=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set SUPABASE_URL=https://your-project.supabase.co
heroku config:set SUPABASE_KEY=<your-key>
heroku config:set SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
heroku config:set SMTP_SERVER=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USERNAME=your-email@gmail.com
heroku config:set SMTP_PASSWORD=<your-app-password>
heroku config:set EMAIL_FROM=noreply@yourdomain.com

# 5. Create Procfile
echo "web: gunicorn --bind 0.0.0.0:\$PORT --workers 4 --timeout 120 app:app" > Procfile

# 6. Deploy
git push heroku main
```

### Using Railway.app

```bash
# 1. Connect GitHub repository
# https://railway.app

# 2. Add environment variables via dashboard
# Copy all from .env.example

# 3. Connect Supabase database
# Railway will auto-detect Procfile

# 4. Deploy (automatic on git push)
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - PEPPER=${PEPPER}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - EMAIL_FROM=${EMAIL_FROM}
    volumes:
      - ./logs:/app/logs
```

---

## Security Hardening Checklist

### Before First Deployment
- [ ] Generate strong SECRET_KEY (32+ random chars)
- [ ] Generate strong PEPPER (32+ random chars)
- [ ] Set FLASK_ENV=production
- [ ] Set FLASK_DEBUG=False
- [ ] Configure valid SMTP credentials
- [ ] Test email sending
- [ ] Test password hashing
- [ ] Test CSRF protection
- [ ] Test rate limiting

### Database Security
- [ ] Create users table with proper schema
- [ ] Create indexes on frequently queried columns
- [ ] Enable database backups
- [ ] Test restore procedures
- [ ] Implement database encryption (Supabase: at-rest encryption enabled)
- [ ] Use service role key only on backend
- [ ] Never expose anon key with elevated permissions

### Application Security
- [ ] Enable HTTPS/SSL (automatic on Heroku/Railway)
- [ ] Configure security headers (automatic via Flask-Talisman)
- [ ] Test all authentication flows
- [ ] Test rate limiting
- [ ] Review logs for suspicious activity
- [ ] Set up monitoring/alerting
- [ ] Test error pages (don't reveal sensitive info)
- [ ] Validate all error messages for information leakage

### Email Security
- [ ] Use app-specific password (not main password)
- [ ] Enable 2FA on email account
- [ ] Configure SPF/DKIM/DMARC records
- [ ] Test email deliverability
- [ ] Monitor email logs for bounces

### Monitoring & Logging
- [ ] Set up log aggregation (e.g., Papertrail, Datadog)
- [ ] Create alerts for:
  - Multiple failed logins
  - Rate limit exceeded
  - Account lockouts
  - Email verification failures
  - Password reset attempts
- [ ] Monitor application errors
- [ ] Review logs daily for anomalies

---

## Environment Variables Reference

```env
# Flask Configuration
FLASK_ENV=production              # or development
FLASK_DEBUG=False                 # Never True in production
SECRET_KEY=                       # 32+ random hex chars for session encryption

# Supabase Configuration  
SUPABASE_URL=                     # https://your-project.supabase.co
SUPABASE_KEY=                     # Anon key (client-side access)
SUPABASE_SERVICE_ROLE_KEY=        # Service role (server-side, KEEP SECRET)

# Security Configuration
PEPPER=                           # 32+ random hex chars for password hashing
CSRF_TOKEN_LENGTH=32              # Bytes of CSRF token randomness

# Rate Limiting
RATE_LIMIT_LOGIN=5 per 15 minutes
RATE_LIMIT_REGISTER=3 per 1 hour
RATE_LIMIT_API=100 per 1 hour

# Email Configuration
SMTP_SERVER=smtp.gmail.com        # Your SMTP server
SMTP_PORT=587                     # Usually 587 (TLS)
SMTP_USERNAME=                    # Your email address
SMTP_PASSWORD=                    # App-specific password
EMAIL_FROM=                       # From address for emails
EMAIL_FROM_NAME=SecureAuth        # Display name

# Token Configuration
VERIFICATION_TOKEN_EXPIRY=24      # Hours
PASSWORD_RESET_TOKEN_EXPIRY=1     # Hours
SESSION_TIMEOUT=30                # Minutes

# Account Lockout
MAX_LOGIN_ATTEMPTS=5              # Attempts before lockout
LOCKOUT_DURATION=1800             # Seconds (30 minutes)

# HTTPS Configuration
ENFORCE_HTTPS=True                # True in production
HSTS_MAX_AGE=31536000             # 1 year in seconds
HSTS_INCLUDE_SUBDOMAINS=True

# Logging Configuration
LOG_LEVEL=INFO                    # INFO, WARNING, ERROR, DEBUG
LOG_FILE=logs/auth.log
LOG_MAX_BYTES=10485760            # 10 MB
LOG_BACKUP_COUNT=10               # Keep 10 rotated logs
```

---

## Common Issues & Solutions

### Email Not Sending
```
Error: SMTPAuthenticationError
Solution: 
- For Gmail: Enable 2FA and create app-specific password
- Check SMTP_SERVER and SMTP_PORT
- Verify SMTP_USERNAME and SMTP_PASSWORD
```

### Database Connection Failed
```
Error: 'connect' to 'supabase.co' port 5432
Solution:
- Verify SUPABASE_URL is correct
- Check SUPABASE_KEY is valid anon key
- Verify Supabase project is running
- Check firewall rules allow outbound connections
```

### HTTPS Redirection Loop
```
Error: Too many redirects
Solution:
- Disable ENFORCE_HTTPS in development
- Ensure your hosting platform terminates SSL before your app
- Check reverse proxy headers configuration
```

### Rate Limiting Not Working
```
Error: Can log in after 5 failed attempts
Solution:
- Restart application (in-memory tracker resets)
- For production, integrate Redis:
  pip install redis
  Update RateLimitTracker to use Redis
```

---

## Performance Optimization

### Database
- Add indexes on frequently queried columns (already done)
- Use database connection pooling
- Monitor slow queries

### Application
- Use gunicorn with multiple workers: `--workers 4`
- Enable gzip compression
- Cache static files
- Monitor CPU and memory usage

### Email
- Consider async email sending with Celery for high volume
- Implement email queue/retry logic

---

## Disaster Recovery

### Backup Strategy
```bash
# Automated daily backups (Supabase does this automatically)
# Manual backup:
pg_dump -h your-db.supabase.co -U postgres database_name > backup.sql
```

### Recovery Procedure
1. Restore database from backup
2. Verify application still connects
3. Test authentication flows
4. Monitor logs for errors
5. Alert users if data loss occurred

---

## Security Updates

### Keep Dependencies Updated
```bash
pip list --outdated
pip install --upgrade package-name
```

### Monitor Security Advisories
- Flask: https://flask.palletsprojects.com/security/
- Bcrypt: https://github.com/pyca/bcrypt
- OWASP Top 10: https://owasp.org/www-project-top-ten/

### Regular Security Audits
- Review logs monthly
- Test all authentication flows
- Attempt common attack vectors
- Check for information leakage

---

## Questions?

Review the code comments in:
- `security.py` - All security algorithms explained
- `app.py` - Route-by-route security details
- `middleware.py` - Logging and header implementation
- `config.py` - Configuration and validation

**Security is a journey, not a destination. Keep learning!** 🔒
