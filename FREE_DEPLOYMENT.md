# Free Deployment Guide - Render + MongoDB Atlas

## Total Cost: $0/month

---

## Step 1: Push Code to GitHub

```
bash
# In your project folder
git init
git add .
git commit -m "Ready for deployment"
git branch -M main
git remote add origin https://github.com/yourusername/learnhub.git
git push -u origin main
```

---

## Step 2: Setup MongoDB Atlas (Free)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Click "Build a Database" → **Free Tier**
3. Create cluster (M0) - Select AWS, nearest region
4. **Database Access** → Create user:
   - Username: `learnhub`
   - Password: Create and save it!
5. **Network Access** → Add IP: `0.0.0.0/0`
6. **Database** → Connect → Drivers
7. Copy connection string:
```
mongodb+srv://learnhub:YOUR_PASSWORD@cluster0.xyz.mongodb.net/learnhub?retryWrites=true&w=majority
```

---

## Step 3: Deploy to Render (Free)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name:** learnhub
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT`
5. **Advanced** → Add Environment Variables:
   
```
   DATABASE_URL=mongodb+srv://learnhub:YOUR_PASSWORD@cluster0.xyz.mongodb.net/learnhub?retryWrites=true&w=majority
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   
```
6. Click **Create Web Service**

---

## Step 4: Generate Secret Key

```
bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and use it as SECRET_KEY in Render.

---

## Step 5: Initialize Database

After deployment, visit:
```
https://your-app-name.onrender.com/create_tables
```

---

## That's It! 🎉

Your app is live at: `https://your-app-name.onrender.com`

---

## Important Notes for Free Tier:

- App sleeps after 15 minutes of inactivity
- Wakes up when accessed (takes ~30 seconds)
- 750 free hours/month
- MongoDB Atlas free tier: 512MB storage

---

## If You Need More Resources:

Upgrade to Render Paid ($7/month) for:
- No cold starts
- Always-on
- More memory
