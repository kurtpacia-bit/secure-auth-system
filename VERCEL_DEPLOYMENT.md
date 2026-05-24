# 🚀 Deploying SecureAuth to Vercel

## ⚠️ Important: Read This First

Vercel is optimized for serverless functions and static sites. Flask apps work, but **have limitations**:

- ❌ **In-memory rate limiting won't work** (state not shared across serverless instances)
- ❌ **Session management is limited** (no persistent file storage)
- ❌ **Background tasks not supported**
- ✅ Database queries work (Supabase handles persistence)
- ✅ Email sending works (SMTP over HTTPS)
- ✅ Authentication flow works
- ✅ Password hashing works

### 🎯 Recommended Alternatives (Better for Flask)
If you need all features including in-memory rate limiting:
- **Railway.app** - Best for Flask, $5/month starting
- **Heroku** - Free tier available, simple setup
- **Fly.io** - Global deployment, reasonable pricing
- **DigitalOcean App Platform** - $12/month, reliable

---

## Deploy to Vercel (If You Want To)

### Step 1: Install Vercel CLI

```powershell
npm install -g vercel
```

### Step 2: Login to Vercel

```powershell
vercel login
```

Creates account at vercel.com if needed.

### Step 3: Push Code to GitHub

```powershell
git init
git add .
git commit -m "Initial commit: SecureAuth system"
git remote add origin https://github.com/yourusername/secure-auth-system.git
git branch -M main
git push -u origin main
```

### Step 4: Configure Environment Variables

Option A: Via CLI
```powershell
vercel env add FLASK_ENV production
vercel env add SECRET_KEY <your-64-char-hex>
vercel env add PEPPER <your-64-char-hex>
vercel env add SUPABASE_URL https://your-project.supabase.co
vercel env add SUPABASE_KEY <your-anon-key>
vercel env add SUPABASE_SERVICE_ROLE_KEY <your-service-role-key>
vercel env add SMTP_SERVER smtp.gmail.com
vercel env add SMTP_PORT 587
vercel env add SMTP_USERNAME your-email@gmail.com
vercel env add SMTP_PASSWORD <your-app-password>
vercel env add EMAIL_FROM noreply@yourdomain.com
```

Option B: Via Vercel Dashboard
1. Go to vercel.com → Project Settings → Environment Variables
2. Add all variables from `.env.example`

### Step 5: Deploy

```powershell
vercel --prod
```

Your app will be live at `https://your-project.vercel.app`

---

## After Deployment

### Fix Rate Limiting (Required for Vercel)

Edit `security.py` to use a database-backed rate limiter instead of in-memory:

```python
# In security.py, replace RateLimitTracker class with this:

class RateLimitTracker:
    """
    Database-backed rate limiting for Vercel (stateless).
    For local development, use in-memory tracker above.
    """
    
    def __init__(self):
        from supabase import create_client
        import os
        self.client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
    
    def check_rate_limit(self, key, max_attempts, window_seconds):
        """Check rate limit using Supabase"""
        # Store attempts in 'rate_limits' table
        # This requires creating the table first
        pass  # Implementation below
```

**Better solution**: Use Supabase to track rate limits. Create this table:

```sql
CREATE TABLE rate_limits (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    key VARCHAR(255) NOT NULL,
    attempts INT DEFAULT 1,
    first_attempt TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rate_limits_key ON rate_limits(key);
CREATE INDEX idx_rate_limits_updated ON rate_limits(updated_at);
```

Then update `security.py`:
```python
def check_rate_limit(self, key, max_attempts, window_seconds):
    """Check rate limit using Supabase instead of in-memory"""
    from datetime import datetime, timedelta
    
    # Get existing record
    response = self.client.table('rate_limits').select('*').eq('key', key).execute()
    
    now = datetime.now()
    
    if response.data:
        record = response.data[0]
        first_attempt = datetime.fromisoformat(record['first_attempt'])
        
        # Check if window has expired
        if now - first_attempt > timedelta(seconds=window_seconds):
            # Reset counter
            self.client.table('rate_limits').update({
                'attempts': 1,
                'first_attempt': now,
                'updated_at': now
            }).eq('key', key).execute()
            return (True, max_attempts - 1)
        
        # Window still active
        attempts = record['attempts']
        if attempts < max_attempts:
            self.client.table('rate_limits').update({
                'attempts': attempts + 1,
                'updated_at': now
            }).eq('key', key).execute()
            return (True, max_attempts - attempts - 1)
        else:
            return (False, 0)
    else:
        # First attempt
        self.client.table('rate_limits').insert({
            'key': key,
            'attempts': 1,
            'first_attempt': now,
            'updated_at': now
        }).execute()
        return (True, max_attempts - 1)
```

### Test Your Deployment

1. Visit your Vercel URL in browser
2. Register a new account
3. Check email for verification link
4. Verify email by clicking link
5. Login and see dashboard
6. Test password reset

### Monitor Logs

```powershell
vercel logs
```

---

## Known Issues on Vercel

| Issue | Solution |
|-------|----------|
| Rate limiting resets between requests | Use Supabase `rate_limits` table (see above) |
| Sessions not persistent | Vercel is stateless - add "remember me" via JWT tokens |
| Logs disappear after 1 hour | Set up log aggregation (Datadog, LogRocket, etc.) |
| Cold starts (slow) | Normal for serverless - first request slower |

---

## Performance Tips

1. **Enable caching** in vercel.json:
```json
{
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000"
        }
      ]
    }
  ]
}
```

2. **Use connection pooling** for Supabase (already in code)

3. **Optimize images** in templates

4. **Use gzip compression** (Vercel does automatically)

---

## Billing

- **Free tier**: 100 GB bandwidth/month, enough for small projects
- **Pro ($20/month)**: Unlimited bandwidth, priority support
- **Enterprise**: Custom pricing

---

## Custom Domain (Optional)

1. Buy domain (Namecheap, GoDaddy, etc.)
2. In Vercel dashboard → Project Settings → Domains
3. Add your custom domain
4. Update DNS records as shown in Vercel

---

## Deploy from GitHub (Automatic)

Instead of `vercel --prod`:

1. Push code to GitHub
2. Connect GitHub repo to Vercel (one-time setup)
3. Vercel auto-deploys on every push to `main`

```powershell
git push origin main
# Vercel automatically deploys!
```

---

## Troubleshooting

### "Module not found"
```
Solution: Add to vercel.json:
{
  "buildCommand": "pip install -r requirements.txt",
  "outputDirectory": "."
}
```

### "Environment variables not loaded"
```
Solution: Ensure variables in Vercel dashboard match .env.example
Check: vercel env list
```

### "Supabase connection fails"
```
Solution: 
1. Verify SUPABASE_URL and SUPABASE_KEY in dashboard
2. Check that Supabase project is running
3. Test locally: python app.py
```

### "Email not sending"
```
Solution:
1. Verify SMTP credentials in environment variables
2. Check SMTP_PORT is 587 (TLS)
3. For Gmail: Make sure app password is used (not main password)
```

---

## Summary

✅ **Vercel is good for:**
- Quick deployments
- Free tier available
- Custom domains
- Automatic HTTPS
- Fast CDN

❌ **Vercel limitations for Flask:**
- Stateless (rate limiting workaround needed)
- Cold starts possible
- No background jobs

🎯 **Better choice for this project:**
- **Railway.app** - Recommended, works out-of-box
- **Heroku** - Easy, familiar, free tier ending soon
- **Fly.io** - Global, modern, scaling friendly

---

**Need help with Railway or Heroku instead?** Much simpler for Flask apps! 🚀
