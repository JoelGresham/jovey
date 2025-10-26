# 🚀 Jovey Setup Instructions
## Your Next Steps to Get Everything Running

**Status:** Backend and Frontend scaffolding complete! ✅
**What's left:** Supabase setup + environment variables + first run

---

## ✅ What's Already Done

- ✅ Backend FastAPI structure created
- ✅ Frontend React + Vite created
- ✅ All dependencies defined
- ✅ Database schema SQL ready
- ✅ Configuration files created
- ✅ Directory structures set up

---

## 🎯 What You Need To Do Now

### Step 1: Create Supabase Project (5 minutes)

1. **Go to:** https://supabase.com
2. **Sign in** with your account
3. **Click:** "New Project"
4. **Fill in:**
   - Name: `jovey`
   - Database Password: (create strong password - SAVE THIS!)
   - Region: Choose closest to you
   - Plan: Free tier is fine
5. **Click:** "Create new project"
6. **Wait:** ~2 minutes for project to be created

### Step 2: Get Your Supabase Credentials

Once your project is created:

1. **Go to:** Project Settings (gear icon) → API
2. **Copy these 3 values:**
   - **Project URL** (example: https://xxxxx.supabase.co)
   - **anon public** key (click "Reveal" if hidden)
   - **service_role** key (click "Reveal" if hidden)

**SAVE THESE! You'll need them in the next step.**

---

## 💻 Installation Commands

### Backend Setup

```bash
# Navigate to backend
cd ~/projects/jovey/backend

# Option 1: Run setup script (recommended)
./setup.sh

# Option 2: Manual setup
conda create -n jovey python=3.11 -y
conda activate jovey
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# NOW EDIT .env with your credentials (see Step 3)
nano .env  # or use VS Code
```

### Frontend Setup

```bash
# Dependencies already installed! Just need to create .env

cd ~/projects/jovey/frontend

# Create .env file
cp .env.example .env

# Edit .env with your credentials (see Step 3)
nano .env  # or use VS Code
```

---

## 📝 Step 3: Configure Environment Variables

### Backend `.env` File

Edit: `/home/gresh/projects/jovey/backend/.env`

```bash
# Supabase Configuration (PASTE YOUR VALUES HERE)
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_KEY=your-anon-public-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Anthropic Claude API (you already have this)
ANTHROPIC_API_KEY=your-anthropic-key-from-bashrc

# Application Configuration
APP_ENV=development
DEBUG=true

# JWT Configuration (generate a random secret)
JWT_SECRET=generate-a-random-string-here-use-openssl-rand-base64-32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**To generate JWT secret:**
```bash
openssl rand -base64 32
```

### Frontend `.env` File

Edit: `/home/gresh/projects/jovey/frontend/.env`

```bash
# Supabase Configuration (SAME VALUES AS BACKEND)
VITE_SUPABASE_URL=https://YOUR-PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-public-key-here

# API Configuration
VITE_API_URL=http://localhost:8000

# Environment
VITE_APP_ENV=development
```

---

## 🗄️ Step 4: Set Up Database Schema

Once you have Supabase credentials:

1. **Go to:** Your Supabase Dashboard
2. **Click:** SQL Editor (left sidebar)
3. **Click:** "New Query"
4. **Copy-paste:** The entire contents of `backend/database/schema.sql`
5. **Click:** "Run" (or press Ctrl+Enter)
6. **Verify:** You should see "Success" message
7. **Check:** Go to Table Editor - you should see:
   - events
   - user_profiles
   - products
   - dealer_product_pricing

---

## 🎉 Step 5: Start the Application!

### Terminal 1: Start Backend

```bash
cd ~/projects/jovey/backend
conda activate jovey
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     🚀 Jovey API starting up...
INFO:     📍 Docs available at: http://localhost:8000/docs
INFO:     Application startup complete.
```

### Terminal 2: Start Frontend

```bash
cd ~/projects/jovey/frontend
npm run dev
```

**Expected output:**
```
VITE v5.x.x ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## ✅ Verification Checklist

Open your browser and check:

- [ ] **Backend API:** http://localhost:8000
  - Should see: `{"message": "Jovey API", "version": "0.1.0", "status": "online"}`

- [ ] **Backend Docs:** http://localhost:8000/docs
  - Should see: FastAPI auto-generated API documentation

- [ ] **Backend Health:** http://localhost:8000/health
  - Should see: `{"status": "healthy"}`

- [ ] **Frontend:** http://localhost:5173
  - Should see: React + Vite welcome page

---

## 🐛 Troubleshooting

### Backend won't start

**Problem:** Port 8000 already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Problem:** Module not found
```bash
# Make sure you're in correct directory and environment
conda activate jovey
cd ~/projects/jovey/backend
pip install -r requirements.txt
```

**Problem:** Supabase connection error
- Check your `.env` file has correct credentials
- Check Supabase project is running (not paused)
- Verify no typos in SUPABASE_URL and SUPABASE_KEY

### Frontend won't start

**Problem:** Dependencies missing
```bash
cd ~/projects/jovey/frontend
npm install
```

**Problem:** Can't connect to backend
- Check `.env` has `VITE_API_URL=http://localhost:8000`
- Check backend is running
- Check CORS configuration in `backend/app/main.py`

---

## 🎓 What To Do Next (After Everything Works)

Once both backend and frontend are running:

### 1. Explore the API Documentation
- Go to http://localhost:8000/docs
- Try the `/health` endpoint
- See all available endpoints

### 2. Test Supabase Connection
We'll create a simple test page to verify Supabase works

### 3. Build Authentication Flow
- Login page
- Register page
- Protected routes

### 4. Start Building Functions
- Database Manager
- Category Management
- etc.

---

## 📚 Reference

### Daily Workflow Commands

```bash
# Terminal 1: Backend
cd ~/projects/jovey/backend
conda activate jovey
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd ~/projects/jovey/frontend
npm run dev

# Terminal 3: Development work
cd ~/projects/jovey
code .  # Open in VS Code
```

### Important URLs

- **Backend API:** http://localhost:8000
- **Backend Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:5173
- **Supabase Dashboard:** https://supabase.com/dashboard

### Important Files

- **Backend .env:** `backend/.env`
- **Frontend .env:** `frontend/.env`
- **Database Schema:** `backend/database/schema.sql`
- **Backend Main:** `backend/app/main.py`
- **Frontend Main:** `frontend/src/main.jsx`

---

## 🚨 Important Notes

1. **Never commit .env files to Git!** (Already in .gitignore)
2. **Save your Supabase credentials securely**
3. **Keep both terminal windows open** while developing
4. **Hot reload works** - changes auto-refresh

---

## 💪 You're Almost There!

Complete the steps above and you'll have:
- ✅ Running FastAPI backend
- ✅ Running React frontend
- ✅ Connected to Supabase database
- ✅ Ready to start building features!

**Estimated time:** 15-20 minutes to complete all setup steps

---

## 🆘 Need Help?

If you get stuck:

1. Check the troubleshooting section above
2. Review the error message carefully
3. Check logs in terminal windows
4. Verify .env files have correct values
5. Make sure Supabase project is created and active

**Common issue:** Typo in environment variables - double-check spelling!

---

**Ready to proceed?** Follow the steps above, then come back and we'll start building the authentication flow!
