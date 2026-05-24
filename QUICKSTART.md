# 🚀 Quick Start Guide - Windows PowerShell

## Step 1: Navigate to Project
```powershell
cd "C:\Users\kurtj\OneDrive\Desktop\Secure-Auth-System"
```

## Step 2: Create Virtual Environment
```powershell
python -m venv venv
```

## Step 3: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your PowerShell prompt.

## Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

This will install:
- Flask 3.0.0
- Supabase 2.4.1
- bcrypt 4.1.2
- Flask-Talisman 1.1.0
- Flask-Limiter 3.5.0
- python-dotenv 1.0.0
- gunicorn 21.2.0

## Step 5: Configure Environment Variables
```powershell
Copy-Item ".env.example" ".env"
```

Now edit `.env` with:
- **SUPABASE_URL**: Get from https://supabase.com dashboard
- **SUPABASE_KEY**: Get from Supabase Settings > API > anon key
- **SUPABASE_SERVICE_ROLE_KEY**: Get from Supabase Settings > API > service_role key
- **SECRET_KEY**: Run `python -c "import secrets; print(secrets.token_hex(32))"`
- **PEPPER**: Run `python -c "import secrets; print(secrets.token_hex(32))"`
- **SMTP_SERVER**: smtp.gmail.com (or your email provider)
- **SMTP_PORT**: 587
- **SMTP_USERNAME**: your-email@gmail.com
- **SMTP_PASSWORD**: Your app-specific password (not your main password!)
- **EMAIL_FROM**: noreply@yourdomain.com

## Step 6: Create Supabase Table
Go to Supabase Dashboard > SQL Editor and paste this:

```sql
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

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_verification_token ON users(verification_token_hash);
CREATE INDEX idx_users_reset_token ON users(password_reset_token_hash);
```

## Step 7: Run the Application
```powershell
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Press CTRL+C to quit
```

## Step 8: Test the System
Open http://localhost:5000 in your browser and:

1. **Register**: Create a new account with a valid email
2. **Verify Email**: Check your email and click the verification link
3. **Login**: Use your username and password
4. **Dashboard**: Should see protected page with all 10 security features
5. **Test Password Reset**: Click "Forgot Password" and follow the flow
6. **Test Account Lockout**: Try 5+ wrong passwords and get locked out

## Troubleshooting

### "python: can't open file 'app.py'"
- Make sure you're in the `Secure-Auth-System` directory
- Run `cd "C:\Users\kurtj\OneDrive\Desktop\Secure-Auth-System"`

### "No module named 'flask'"
- Make sure virtual environment is activated (see Step 3)
- Look for `(venv)` at the start of your PowerShell prompt
- Run `pip install -r requirements.txt` again

### "Cannot find path '.env.example'"
- Make sure you're in the right directory
- Run `dir` and you should see `.env.example` listed

### Supabase Connection Error
- Check that SUPABASE_URL in .env is correct (should end in `.supabase.co`)
- Verify SUPABASE_KEY matches your anon key from Supabase dashboard
- Make sure you created the `users` table

### Email Not Sending
- For Gmail: Enable 2-Factor Authentication and create an [App Password](https://support.google.com/accounts/answer/185833)
- Use the app password in `.env` as SMTP_PASSWORD (not your main password!)
- Verify SMTP_SERVER and SMTP_PORT are correct

## Default Credentials (for testing only!)
After running the SQL above, you can test with:
```
Username: testuser
Password: TestPass123!
Email: test@example.com
```

(This user doesn't exist yet - register one instead!)

## Next Steps
- Read `README.md` for feature overview
- Read `DEPLOYMENT_GUIDE.md` for production deployment
- Review code comments in `security.py` and `app.py` for implementation details

**Questions? Check the code - every security feature is thoroughly commented!** 🔐
