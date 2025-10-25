# 🚂 Railway Deployment Guide

## ✅ Railway Supports Python!

Railway **fully supports** Python applications, including:
- ✅ Python 3.13
- ✅ Multiple services (Python + Next.js)
- ✅ Background processes
- ✅ Environment variables
- ✅ SQLite (with persistent volumes)

---

## 📦 Deployment Strategy

### Architecture on Railway

```
┌─────────────────────────────────────────────┐
│              Railway Project                │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────┐  ┌──────────────────┐ │
│  │   Service 1     │  │   Service 2      │ │
│  │   (Backend)     │  │   (Frontend)     │ │
│  │                 │  │                  │ │
│  │ - Python 3.13   │  │ - Next.js 14     │ │
│  │ - FastAPI/Flask │  │ - React 18       │ │
│  │ - SQLite        │  │ - Tailwind       │ │
│  │ - conversation_ │  │ - Web UI         │ │
│  │   processor.py  │  │                  │ │
│  └─────────────────┘  └──────────────────┘ │
│         ↑ Port 8000         ↑ Port 3000    │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │   Shared Volume (for storage/)      │   │
│  │   - conversations.db                │   │
│  │   - signal files                    │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Setup Files

### 1. Create `Procfile` (for Python backend)

```bash
# Procfile (root directory)
web: python conversation_processor.py
```

### 2. Create `railway.json` (optional)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3. Update `conversation_processor.py` for Railway

Add health check endpoint:

```python
# At the end of conversation_processor.py
if __name__ == '__main__':
    # For Railway health checks
    import os
    port = int(os.getenv('PORT', 8000))
    
    # Start processor
    processor = ConversationProcessor()
    
    # Optional: Add simple HTTP health check
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(404)
                self.end_headers()
    
    # Start health check server in background
    health_server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    health_thread = threading.Thread(target=health_server.serve_forever, daemon=True)
    health_thread.start()
    
    print(f"🏥 Health check server started on port {port}")
    
    # Run processor
    processor.run()
```

### 4. Update `requirements.txt`

Make sure all dependencies are listed:

```txt
python-dotenv==1.0.0
pydantic>=2.5.0
rich==13.7.0
typer==0.12.3
watchdog==3.0.0
openai>=1.54.0
google-generativeai>=0.8.0
```

### 5. Create `.railwayignore`

```
# Railway Ignore
node_modules/
.next/
.git/
*.log
__pycache__/
*.pyc
.env.local
.DS_Store
```

---

## 🚀 Deployment Steps

### Step 1: Create Railway Project

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Choose **"Deploy from GitHub repo"**
5. Select your repository

### Step 2: Create Two Services

#### Service 1: Python Backend

1. Click **"+ New Service"**
2. Select **"GitHub Repo"**
3. Configure:
   ```
   Name: backend
   Root Directory: /
   Build Command: pip install -r requirements.txt
   Start Command: python conversation_processor.py
   ```

4. Add Environment Variables:
   ```
   ZAI_API_KEY=your_key_here
   ZAI_BASE_URL=https://api.z.ai/api/coding/paas/v4
   GEMINI_API_KEY=your_key_here
   GLM_MODEL=glm-4.5-air
   GEMINI_MODEL=gemini-2.5-flash
   MAX_TURN_LENGTH=10000
   PORT=8000
   ```

#### Service 2: Next.js Frontend

1. Click **"+ New Service"**
2. Select **"GitHub Repo"**
3. Configure:
   ```
   Name: frontend
   Root Directory: /web
   Build Command: npm install && npm run build
   Start Command: npm start
   ```

4. Add Environment Variables:
   ```
   NODE_ENV=production
   PORT=3000
   ```

### Step 3: Add Shared Volume (for SQLite)

1. Go to backend service
2. Click **"Settings"** → **"Volumes"**
3. Add volume:
   ```
   Mount Path: /app/storage
   Size: 1 GB
   ```

### Step 4: Connect Services

Update Next.js API routes to use backend service URL:

```typescript
// web/app/api/sessions/start/route.ts
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'
```

Add to frontend environment variables:
```
BACKEND_URL=https://your-backend.railway.app
```

---

## 🔧 Alternative: Single Service (Simpler)

If you want to deploy as a single service:

### Create `start.sh` for Railway

```bash
#!/bin/bash

# Start conversation processor in background
python conversation_processor.py &

# Wait a bit for processor to initialize
sleep 5

# Start Next.js frontend
cd web
npm start
```

### Update `Procfile`

```
web: bash start.sh
```

### Railway Configuration

```
Root Directory: /
Build Command: pip install -r requirements.txt && cd web && npm install && npm run build
Start Command: bash start.sh
```

---

## 📝 Environment Variables Setup

In Railway Dashboard → Settings → Variables:

```bash
# Required
ZAI_API_KEY=bfc0ba4defa24b909bae2fdce3f7802e.cia5P6s2JimydvkQ
GEMINI_API_KEY=AIzaSyCWm17KwleaDf6cfdwz_l6pEOlFjtbtuos

# Optional (with defaults)
ZAI_BASE_URL=https://api.z.ai/api/coding/paas/v4
GLM_MODEL=glm-4.5-air
GEMINI_MODEL=gemini-2.5-flash
MAX_TURN_LENGTH=10000
PORT=8000
```

---

## 🔍 Health Checks

Railway will automatically health check your service. Make sure:

1. Backend responds to HTTP requests on `PORT`
2. Frontend serves on port 3000
3. Both services start within 5 minutes

---

## 📊 Monitoring

Railway provides:
- ✅ Real-time logs
- ✅ Metrics (CPU, Memory, Network)
- ✅ Deployment history
- ✅ Environment variables management

---

## 💰 Pricing

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month
- **Pro Plan**: $20/month
- Includes:
  - Shared CPU
  - 512 MB RAM (Hobby) / 8 GB RAM (Pro)
  - Persistent storage
  - Custom domains

---

## 🐛 Troubleshooting

### Issue: SQLite database not persisting

**Solution**: Add a volume to your service
```
Mount Path: /app/storage
```

### Issue: Port binding error

**Solution**: Use Railway's `PORT` environment variable
```python
port = int(os.getenv('PORT', 8000))
```

### Issue: Build fails

**Solution**: Check Python version in `runtime.txt`
```
python-3.13.0
```

### Issue: Frontend can't connect to backend

**Solution**: Use Railway's internal networking
```typescript
const BACKEND_URL = process.env.RAILWAY_PRIVATE_DOMAIN 
  ? `http://${process.env.RAILWAY_PRIVATE_DOMAIN}`
  : 'http://localhost:8000'
```

---

## 🎯 Recommended Setup

### For Production:

**Two Services Approach** (Recommended)
- Service 1: Python backend (with volume for storage/)
- Service 2: Next.js frontend
- Better separation of concerns
- Easier to scale

### For Testing:

**Single Service Approach**
- One service running both
- Simpler deployment
- Good for proof-of-concept

---

## 📚 Next Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "feat: prepare for Railway deployment"
   git push origin main
   ```

2. **Create Railway Project**
   - Connect GitHub repo
   - Configure services
   - Add environment variables

3. **Deploy**
   - Railway auto-deploys on push
   - Monitor logs
   - Test application

4. **Custom Domain** (optional)
   - Railway provides: `your-app.railway.app`
   - Add custom domain in settings

---

## ✅ Checklist

- [ ] Create `Procfile`
- [ ] Update `conversation_processor.py` with health check
- [ ] Verify `requirements.txt` is complete
- [ ] Create `.railwayignore`
- [ ] Push to GitHub
- [ ] Create Railway project
- [ ] Configure services
- [ ] Add environment variables
- [ ] Add volume for storage/
- [ ] Deploy and test
- [ ] Monitor logs

---

**Railway Documentation**: https://docs.railway.app  
**Python on Railway**: https://docs.railway.app/languages/python  
**Status**: ✅ Ready to Deploy!

