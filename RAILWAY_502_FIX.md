# 🐛 Railway 502 Troubleshooting

## Current Issue: 502 Bad Gateway

### ✅ Quick Fix Options

#### **Option 1: Deploy Next.js Only (Simplest)**

Update `Procfile`:
```
web: bash railway-simple.sh
```

This starts ONLY Next.js. Python backend can be added later as a separate service.

#### **Option 2: Check Railway Logs**

In Railway Dashboard:
1. Go to **Deployments**
2. Click latest deployment
3. Check **Deploy Logs**

Look for:
- ❌ "npm start" errors
- ❌ Port binding errors
- ❌ "Address already in use"

#### **Option 3: Environment Variables**

Make sure these are set in Railway:
```
PORT=3000
NODE_ENV=production
ZAI_API_KEY=your_key
GEMINI_API_KEY=your_key
```

---

## 🔍 Common Causes of 502

### 1. **App Not Binding to 0.0.0.0**
✅ **FIXED**: `next start -H 0.0.0.0`

### 2. **App Not Using Railway's PORT**
✅ **FIXED**: `next start -p ${PORT:-3000}`

### 3. **App Crashes on Startup**
Check logs for errors

### 4. **App Takes Too Long to Start**
Railway timeout = 5 minutes

### 5. **Multiple Processes Fighting for Port**
Try Next.js only first

---

## 🚀 Recommended: Two Services Approach

Instead of running both in one container, deploy separately:

### **Service 1: Frontend (Next.js)**
```
Name: plan-agents-frontend
Root: /web
Build: npm install && npm run build
Start: npm start
Port: 3000
```

### **Service 2: Backend (Python)**
```
Name: plan-agents-backend
Root: /
Build: pip install -r requirements.txt
Start: python conversation_processor.py
Port: 8000
```

Connect them via Railway's internal networking.

---

## 🧪 Test Locally First

```bash
# Build
cd web && npm run build

# Test start command
npm start

# Should see:
# ▲ Next.js 14.0.4
# - Local:        http://localhost:3000
# - Network:      http://0.0.0.0:3000
```

If this works locally, it should work on Railway.

---

## 📝 Current Files Status

| File | Purpose | Status |
|------|---------|--------|
| `railway-start.sh` | Both services | ✅ Updated |
| `railway-simple.sh` | Next.js only | ✅ NEW |
| `Procfile` | Entry point | Update to: `web: bash railway-simple.sh` |
| `Dockerfile` | Build config | ✅ OK |
| `web/package.json` | Start command | ✅ Fixed |

---

## ⚡ Quick Actions

### 1. Try Simple Version First
```bash
# Update Procfile
echo "web: bash railway-simple.sh" > Procfile

git add .
git commit -m "fix: simplified Railway startup"
git push
```

### 2. Check if Port 3000 is Correct
Railway → Settings → Networking → Port: **3000** ✅

### 3. View Live Logs
Railway → Deployments → View Logs → Look for errors

---

## 🆘 If Still 502

**Option A: Use Railway's Auto-Config**

Delete these files and let Railway auto-detect:
- Remove `Procfile`
- Remove `railway.json`
- Keep only `web/package.json` with fixed start command

**Option B: Deploy as Two Separate Services**

See "Two Services Approach" above.

**Option C: Check Health**

Railway expects HTTP 200 response. Make sure Next.js is actually starting.

---

## ✅ Expected Working Logs

```
🚂 Starting Next.js...
📁 Storage created
⚛️  Starting Next.js on PORT 3000...

> plan-agents-web@1.0.0 start
> next start -H 0.0.0.0 -p 3000

▲ Next.js 14.0.4
- Local:        http://localhost:3000
- Network:      http://0.0.0.0:3000

✓ Ready in 1234ms
```

If you see this → App should be accessible!

---

**Status**: Debugging 502...  
**Next**: Try simplified version or check logs

