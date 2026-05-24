# 🆓 Deploy to Render.com (Completely FREE)

**Best free option for Flask apps!** Render.com has:
- ✅ Completely free tier (no credit card required)
- ✅ Stateful (rate limiting works)
- ✅ Auto-deploy from GitHub
- ✅ Free PostgreSQL database included
- ✅ All features work perfectly
- ✅ Up to 750 hours/month (enough for always-on)
- ⚠️ Spins down after 15 minutes of inactivity (cold starts)

---

## Quick Deploy (5 Minutes)

### Step 1: Push to GitHub

```powershell
git init
git add .
git commit -m "Initial: SecureAuth"
git remote add origin https://github.com/yourusername/secure-auth-system.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Account

Go to **https://render.com** and sign up with GitHub (recommended).

### Step 3: Create New Web Service

1. Click "New +" → "Web Service"
2. Select "Deploy from GitHub repo"
3. Connect GitHub (one-time)
4. Select `secure-auth-system` repo
5. Fill in these settings:

```
Name: secure-auth-system (or anything)
Environment: Python 3
Region: Choose closest to you
Branch: main
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

### Step 4: Add Environment Variables

Before deploying, add variables:

**In Render dashboard:**
1. Go to "Environment" section
2. Add each variable:

```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
PEPPER=<generate: python -c "import secrets; print(secrets.token_hex(32))">
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=<your-app-password>
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=SecureAuth
```

### Step 5: Deploy

Click "Deploy"

That's it! Your app will be live at `https://secure-auth-system.onrender.com`

---

## Auto-Deploy from GitHub

Once set up, every time you push:

```powershell
git push origin main
# Render automatically deploys!
```

---

## Custom Domain (Free)

1. Buy domain ($10-15/year from Namecheap, Google Domains, etc.)
2. In Render dashboard → Custom Domain
3. Add your domain
4. Update DNS (Render shows instructions)

---

## How to Get Free Supabase Database

You're probably using Supabase already, which is free:
- ✅ Free tier includes 2 projects
- ✅ 500 MB storage
- ✅ 2 GB bandwidth
- ✅ Enough for thousands of users

Just use your existing Supabase project!

---

## How to Get Free Email Sending

### Option 1: Gmail (Recommended - FREE)

1. Enable 2-Factor Authentication on Gmail
2. Generate [App Password](https://support.google.com/accounts/answer/185833)
3. Use in `.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=<your-app-password>
```

### Option 2: SendGrid (FREE up to 100 emails/day)

1. Sign up at sendgrid.com
2. Create API key
3. Use SendGrid SMTP:
```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=<your-sendgrid-api-key>
```

### Option 3: Mailgun (FREE up to 1000 emails/month)

1. Sign up at mailgun.com
2. Get SMTP credentials
3. Use their SMTP server

**For this project: Use Gmail** - it's simplest and free!

---

## Free Tier Limitations

| Feature | Limit | Enough? |
|---------|-------|---------|
| Monthly requests | Unlimited | ✅ Yes |
| Storage | Free tier Supabase | ✅ Yes |
| Bandwidth | Free tier Supabase | ✅ Yes |
| Active hours | 750/month | ✅ Yes (always-on) |
| Cold starts | After 15 min inactivity | ⚠️ First request slow |
| Custom domain | Included | ✅ Yes |

**Cold starts:** First request after 15 mins takes ~5 seconds. Not ideal but acceptable for personal projects.

---

## Wake Up Your App (Optional)

To prevent cold starts, ping your app every 10 minutes:

Use a free service like **UptimeRobot**:
1. Go to uptimerobot.com
2. Create free account
3. Add monitor for `https://your-app.onrender.com`
4. Check every 5 minutes
5. Done!

Your app will never sleep. ✅

---

## Other FREE Options

### Google Cloud Run
- ✅ Free tier: 2 million requests/month
- ✅ Completely serverless
- ✅ Excellent performance
- ⚠️ More complex setup
- 📖 [Cloud Run Guide](https://cloud.google.com/run/docs/quickstarts/build-and-deploy)

### Vercel
- ✅ Free tier: 100 GB bandwidth/month
- ⚠️ Rate limiting needs workaround
- ⚠️ Sessions limited
- 📖 See VERCEL_DEPLOYMENT.md

### PythonAnywhere
- ✅ Free tier: pythonanywhere.com
- ✅ Python-specific
- ⚠️ Limited features
- ⏱️ Takes 30 minutes to set up

---

## Summary

**Best completely FREE option for this project:**

| Platform | Setup | Features | Best For |
|----------|-------|----------|----------|
| **Render** | 5 min | ✅ All work | 🥇 **Best** |
| Google Cloud Run | 15 min | ✅ All work | Global apps |
| Vercel | 10 min | ⚠️ Limited | Frontend apps |
| PythonAnywhere | 30 min | ⚠️ Limited | Beginners |

---

## Cost Breakdown (ZERO)

- **Render**: FREE
- **Supabase**: FREE (up to 2 projects)
- **Gmail/SendGrid**: FREE (enough emails)
- **GitHub**: FREE
- **Custom domain**: ~$10/year (optional)

**Total cost: $0 (or $10/year if you want custom domain)**

---

## Next Steps to Deploy Free

### Option 1: Render.com (Recommended)
1. Go to render.com
2. Sign up with GitHub
3. Create Web Service (follow steps above)
4. Done! Live in ~2 minutes

### Option 2: Google Cloud Run (Advanced)
1. Go to cloud.google.com
2. Create project
3. Deploy from GitHub
4. Done! Live in ~5 minutes

---

## Deploy Now!

Ready? Here's the exact order:

1. **Generate secrets:**
   ```powershell
   python -c "import secrets; print('SECRET_KEY:', secrets.token_hex(32))"
   python -c "import secrets; print('PEPPER:', secrets.token_hex(32))"
   ```

2. **Get Supabase credentials:**
   - URL: Settings → API → Project URL
   - Anon key: Settings → API → anon key
   - Service role: Settings → API → service_role key

3. **Get Gmail credentials:**
   - Enable 2FA: myaccount.google.com/security
   - Create app password: [Link](https://support.google.com/accounts/answer/185833)

4. **Push to GitHub:**
   ```powershell
   git push origin main
   ```

5. **Deploy to Render:**
   - Go to render.com
   - Click "New Web Service"
   - Select your GitHub repo
   - Add environment variables
   - Click "Deploy"

6. **Test your live app!**
   - Register a new account
   - Check email for verification
   - Click verification link
   - Login to dashboard
   - Test password reset

---

## Troubleshooting

**"Build failed"**
- Check that `requirements.txt` exists
- Make sure all files pushed to GitHub

**"Environment variables not loaded"**
- Add to Render environment (not just .env)
- Restart deploy after adding variables

**"Supabase connection failed"**
- Verify SUPABASE_URL format (should end in `.supabase.co`)
- Check SUPABASE_KEY is correct anon key

**"Email not sending"**
- For Gmail: Use app password, not main password
- Verify SMTP_PORT is 587

---

## Questions?

- **Render support**: help.render.com
- **Supabase support**: supabase.com/support
- **GitHub help**: docs.github.com

**You're 10 minutes away from a free, live, secure authentication system!** 🚀
