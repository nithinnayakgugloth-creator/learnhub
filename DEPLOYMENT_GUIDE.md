# LearnHub Production Deployment Guide

## Overview
This guide covers deploying a Flask-based LearnHub application with MongoDB Atlas, optimized for 50+ concurrent users.

---

## Prerequisites
- Git installed locally
- Python 3.10+ installed
- MongoDB Atlas account (free tier works)
- Hosting provider account (see recommendations below)

---

## 1. Hosting Recommendations

### For 50 Concurrent Users - Recommended Options:

| Provider | Plan | Monthly Cost | Specs |
|----------|------|--------------|-------|
| **Render** | Starter | $7/month | 512MB RAM, shared CPU |
| **Railway** | Starter | $5/month | 1GB RAM |
| **DigitalOcean** | Droplet Basic | $6/month | 1GB RAM, 1 vCPU |
| **AWS Lightsail** | Instance | $5/month | 1GB RAM, 1 vCPU |

**Recommendation:** Render or Railway for easiest setup with auto-deploy from GitHub.

---

## 2. MongoDB Atlas Setup

### Step 2.1: Create Cluster
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster (M0 tier)
3. Select AWS as provider, choose region closest to your users

### Step 2.2: Configure Database Access
1. Go to **Database Access** → Add New User
2. Username: `learnhub`
3. Password: Generate secure password
4. Built-in Role: **Read and Write to any database**

### Step 2.3: Network Access
1. Go to **Network Access** → Add IP Address
2. For deployment: Use `0.0.0.0/0` (allow all IPs)
3. For local development: Add your IP

### Step 2.4: Get Connection String
1. **Database** → **Connect** → **Drivers**
2. Copy connection string:
```
mongodb+srv://<username>:<password>@cluster.mongodb.net/learnhub?retryWrites=true&w=majority
```
3. Replace `<username>` and `<password>` with your credentials

---

## 3. Application Configuration

### Step 3.1: Update app.py for Production
Add the following to your `app.py`:

```
python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Production configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['MONGO_URI'] = os.environ.get('DATABASE_URL')

# Force HTTPS in production
@app.before_request
def https_redirect():
    if os.environ.get('FLASK_ENV') == 'production':
        from flask import request, redirect
        if request.is_secure:
            return
        return redirect(request.url.replace('http://', 'https://'), code=301)
```

### Step 3.2: Create Environment File
Create `.env` file (DO NOT commit to Git):
```
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/learnhub?retryWrites=true&w=majority
SECRET_KEY=generate-secure-random-string-here
FLASK_ENV=production
```

Generate secret key:
```
bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 4. Files Created

### requirements.txt
```
Flask==3.0.0
pymongo==4.6.1
gunicorn==21.2.0
python-dotenv==1.0.0
```

### Procfile (for Render/Railway)
```
web: gunicorn app:app --workers 3 --timeout 120 --bind 0.0.0.0:$PORT
```

---

## 5. Deployment Options

### Option A: Deploy to Render (Recommended)

#### Step 5A.1: Push to GitHub
```
bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/learnhub.git
git push -u origin main
```

#### Step 5A.2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Create New → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name:** learnhub
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --workers 3 --timeout 120 --bind 0.0.0.0:$PORT`
5. Add Environment Variables:
   - `DATABASE_URL`: Your MongoDB Atlas connection string
   - `SECRET_KEY`: Your generated secret key
   - `FLASK_ENV`: `production`
6. Click **Deploy Web Service**

#### Step 5A.3: Enable Auto-Deploy
- Render automatically deploys on git push
- Enable "Auto-deploy" in settings

---

### Option B: Deploy to Railway

#### Step 5B.1: Deploy on Railway
1. Go to [Railway Dashboard](https://railway.app)
2. Create New → **Deploy from GitHub repo**
3. Select your repository
4. Add Environment Variables in Variables tab:
   - `DATABASE_URL`: Your MongoDB Atlas connection string
   - `SECRET_KEY`: Your generated secret key
   - `FLASK_ENV`: `production`
5. Deploy will start automatically

---

### Option C: Deploy to DigitalOcean with Nginx

#### Step 5C.1: Create Droplet
```
bash
# Create Droplet via DigitalOcean console
# Choose: Ubuntu 22.04, $6/mo plan
```

#### Step 5C.2: Connect to Server
```
bash
ssh root@your-droplet-ip
```

#### Step 5C.3: Install Dependencies
```
bash
# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install -y python3 python3-pip python3-venv nginx

# Install Certbot for HTTPS
apt install -y certbot python3-certbot-nginx
```

#### Step 5C.4: Deploy Application
```
bash
# Create application directory
mkdir -p /var/www/learnhub
cd /var/www/learnhub

# Clone repository
git clone your-repo-url .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Add DATABASE_URL, SECRET_KEY, FLASK_ENV=production
```

#### Step 5C.5: Create Systemd Service
```bash
nano /etc/systemd/system/learnhub.service
```

Add content:
```
ini
[Unit]
Description=LearnHub Flask Application
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/learnhub
Environment="PATH=/var/www/learnhub/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/var/www/learnhub/venv/bin/gunicorn app:app --workers 3 --timeout 120 --bind 127.0.0.1:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```
bash
systemctl daemon-reload
systemctl enable learnhub
systemctl start learnhub
```

#### Step 5C.6: Configure Nginx
```
bash
# Copy nginx config
cp nginx.conf /etc/nginx/sites-available/learnhub
ln -s /etc/nginx/sites-available/learnhub /etc/nginx/sites-enabled/

# Test nginx config
nginx -t

# Restart nginx
systemctl restart nginx
```

#### Step 5C.7: Setup HTTPS (Let's Encrypt)
```
bash
# Get SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts
# Choose option 2 (Redirect HTTP to HTTPS)

# Auto-renewal (automatic)
certbot renew --dry-run
```

---

## 6. Gunicorn Configuration

### Basic Command (for testing)
```
bash
gunicorn app:app --workers 3 --timeout 120 --bind 0.0.0.0:8000
```

### Optimized for 50 Users
```
bash
gunicorn app:app \
  --workers 3 \
  --worker-class sync \
  --timeout 120 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Production gunicorn.conf.py (Alternative)
Create `gunicorn.conf.py`:
```
python
import multiprocessing

# Workers = 2-4 x CPU cores (for 1CPU, use 2-4)
workers = 3

# Worker class
worker_class = 'sync'

# Timeout in seconds
timeout = 120

# Keep-alive connections
keepalive = 5

# Max requests per worker (helps with memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Bind
bind = '0.0.0.0:8000'
```

Then run:
```
bash
gunicorn -c gunicorn.conf.py app:app
```

---

## 7. Performance Optimization

### For 50 Concurrent Users:

1. **Gunicorn Workers:** 3 workers (2*CPU + 1)
2. **Timeout:** 120 seconds (for slow connections)
3. **Keep-alive:** 5 seconds
4. **Static files:** Served by Nginx (not Flask)

### MongoDB Optimization:
```python
# Connection pooling in app.py
from pymongo import MongoClient
client = MongoClient(os.environ.get('DATABASE_URL'), maxPoolSize=50, minPoolSize=10)
db = client.get_default_database()
```

---

## 8. Monitoring & Auto-Restart

### Systemd Service (auto-restart on crash)
The systemd service configured in Step 5C.5 includes:
- `Restart=always` - Restarts on crash
- `RestartSec=5` - Waits 5 seconds before restart

### Health Check Endpoint
Add to `app.py`:
```
python
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200
```

Configure your hosting to ping `/health` every 30 seconds.

---

## 9. Troubleshooting

### Check Logs
```
bash
# Render
Dashboard → Your Service → Logs

# Railway
Dashboard → Your Project → Deploys → View Logs

# DigitalOcean/Droplet
journalctl -u learnhub -f
```

### Common Issues
| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check if gunicorn is running |
| Database connection error | Verify DATABASE_URL |
| Static files not loading | Check Nginx static alias path |
| Slow response | Increase workers or check DB queries |

---

## 10. Quick Reference Commands

### Local Production Test
```
bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn app:app --workers 3 --bind 0.0.0.0:8000

# Test locally
curl http://localhost:8000/health
```

### Deploy Commands (DigitalOcean)
```
bash
# Pull latest changes
cd /var/www/learnhub && git pull

# Restart app
systemctl restart learnhub

# Check status
systemctl status learnhub
```

---

## Summary

| Component | Configuration |
|-----------|---------------|
| **Web Server** | Gunicorn (3 workers) |
| **Reverse Proxy** | Nginx |
| **Database** | MongoDB Atlas (M0 free tier) |
| **HTTPS** | Let's Encrypt (free) |
| **Auto-restart** | Systemd (Linux) / Platform-managed |
| **Cost** | $0-7/month |

For 50 concurrent users, Render's $7/month plan or Railway's $5/month plan will handle this easily. The free MongoDB Atlas tier is sufficient for this user load.
