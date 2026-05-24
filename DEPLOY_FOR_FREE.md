# ⚡ Deploy for FREE in 10 Minutes

**No credit card required. No monthly costs. Ever.**

---

## What You Need (Get Now)

### 1. GitHub Account (FREE)
- Sign up at github.com if you don't have one

### 2. Supabase Database (FREE)
- You probably already have this
- If not: Create free project at supabase.com
- Get your credentials from Settings → API

### 3. Gmail Account (FREE)
- You definitely have this
- Enable 2-Factor Authentication
- Create [App Password](https://support.google.com/accounts/answer/185833)

### 4. Secret Keys (Generate Now)
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy both outputs - you'll need them in a few minutes.

---

## Step-by-Step Deploy (5 minutes)

### 1. Push Code to GitHub (2 min)

```powershell
cd "C:\Users\kurtj\OneDrive\Desktop\Secure-Auth-System"
git init
git add .
git commit -m "Initial: SecureAuth"
git remote add origin https://github.com/YOUR_USERNAME/secure-auth-system.git
git branch -M main
git push -u origin main
```

**What to do if you get errors:**
- If `git` not installed: Download from git-scm.com
- If `fatal: not a git repository`: You're not in Secure-Auth-System folder
- If `fatal: origin already exists`: Delete `.git` folder and start over

### 2. Create Render Account (1 min)

Go to **https://render.com**
- Click "Sign up"
- Click "Continue with GitHub"
- Authorize Render
- Done!

### 3. Deploy (2 min)

In Render dashboard:
1. Click "New +" → "Web Service"
2. Click "Connect repository"
3. Find and select `secure-auth-system`
4. Fill in:
   - **Name:** `secure-auth-system`
   - **Environment:** `Python 3`
   - **Region:** Pick closest to you
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

5. Scroll down to "Environment" section
6. Add these variables (click "Add Environment Variable" for each):

```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<paste first secret you generated>
PEPPER=<paste second secret you generated>
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=<from Supabase Settings > API > anon key>
SUPABASE_SERVICE_ROLE_KEY=<from Supabase Settings > API > service_role>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=<your-gmail-app-password>
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=SecureAuth
```

7. Click **"Deploy"**

**That's it!** Your app is now live! 🎉

You'll get a URL like: `https://secure-auth-system.onrender.com`

---

## Test Your Live App (1 min)

1. Open the URL from Render
2. Click "Register"
3. Create account with valid email
4. Check email for verification link
5. Click link to verify
6. Login with your credentials
7. See dashboard with all features

---

## What to Do Next

### Keep It Always-On (Optional, 2 min)

After 15 minutes of inactivity, Render spins down (first request becomes slow).

To prevent this, add a free monitor:

1. Go to **https://uptimerobot.com**
2. Sign up (free)
3. Click "Add Monitor"
4. Set:
   - Type: `HTTP(s)`
   - URL: `https://secure-auth-system.onrender.com`
   - Check interval: `5 minutes`
5. Click "Save"

Now your app stays awake 24/7! ✅

### Get Custom Domain (Optional, $10-15/year)

1. Buy domain: namecheap.com, google.com/domains, etc.
2. In Render dashboard → Custom Domain
3. Follow instructions

---

## Auto-Deploy on Code Changes

Every time you push to GitHub, Render auto-deploys:

```powershell
# Make a change to your code
# Then push:
git add .
git commit -m "Your message"
git push origin main

# Render automatically deploys within 1 minute!
```

---

## Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| Render hosting | **FREE** | 750 hours/month |
| Supabase database | **FREE** | 500 MB storage |
| Gmail email | **FREE** | Unlimited emails |
| GitHub | **FREE** | Unlimited repos |
| Custom domain | ~$10/year | Optional |
| **TOTAL** | **$0-10/year** | ✅ Fully free or cheap |

---

## Troubleshooting

**Deploy failed?**
- Check build logs in Render dashboard
- Most likely: missing environment variable

**Can't login?**
- Check email - you might need to verify first
- Look at Supabase dashboard to see if user was created

**Email not arriving?**
- Check spam folder
- Make sure you used app password (not main Gmail password)
- Verify SMTP_USERNAME matches your Gmail

**App is slow?**
- Normal on first request after 15 min (cold start)
- Set up UptimeRobot to keep it warm

---

## You're Done! 🎊

Your SecureAuth system is:
- ✅ Live on the internet
- ✅ Completely free
- ✅ Production-ready
- ✅ Secure (all 10 features active)
- ✅ Auto-deploying

Share your URL with friends!

```
https://secure-auth-system.onrender.com
```

---

## Questions?

- **Render help:** help.render.com
- **Code help:** See comments in app.py
- **Supabase help:** supabase.com/support

**Congratulations on your first deployed app!** 🚀
