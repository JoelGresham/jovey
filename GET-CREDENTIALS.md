# Get Your Supabase Credentials
## Quick Guide for "jovey" Project

**Status:** ✅ Documentation updated - ready to get credentials!

---

## 📋 Step-by-Step: Get Your Credentials

### 1. Go to Your Supabase Project

1. Open: https://supabase.com/dashboard
2. Click on your **"jovey"** project
3. Wait for it to finish initializing (if still setting up)

### 2. Navigate to API Settings

1. Click on the **⚙️ Settings** icon (bottom of left sidebar)
2. Click on **API** in the settings menu

### 3. Copy These 3 Values

You'll see a section called "Project API keys". Copy these:

#### A. Project URL
```
Section: Configuration → Project URL
Example: https://abcdefghijk.supabase.co

Copy the entire URL!
```

#### B. anon public Key
```
Section: Project API keys → anon public
Click "Reveal" if hidden
It's a long string starting with: eyJ...

Copy the entire key!
```

#### C. service_role Key
```
Section: Project API keys → service_role
Click "Reveal" to show it
⚠️ Keep this SECRET - it bypasses Row Level Security!

Copy the entire key!
```

---

## 📝 Now Create Your .env Files

### Backend .env File

```bash
cd ~/projects/jovey/backend

# Create .env file
nano .env
# Or use VS Code: code .env
```

**Paste this and replace with YOUR values:**

```bash
# Supabase Configuration
SUPABASE_URL=https://YOUR-PROJECT-ID.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR-ANON-KEY-HERE
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR-SERVICE-KEY-HERE

# Anthropic Claude API (you already have this)
ANTHROPIC_API_KEY=your-anthropic-key-from-bashrc

# Application Configuration
APP_ENV=development
DEBUG=true

# JWT Configuration (generate with: openssl rand -base64 32)
JWT_SECRET=your-generated-secret-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Generate JWT Secret:**
```bash
openssl rand -base64 32
# Copy the output and paste it as JWT_SECRET
```

**Get Anthropic Key:**
```bash
# You already have this in ~/.bashrc
# Check with:
echo $ANTHROPIC_API_KEY

# If empty, check:
cat ~/.bashrc | grep ANTHROPIC
```

### Frontend .env File

```bash
cd ~/projects/jovey/frontend

# Create .env file
nano .env
# Or: code .env
```

**Paste this and replace with YOUR values:**

```bash
# Supabase Configuration (SAME as backend!)
VITE_SUPABASE_URL=https://YOUR-PROJECT-ID.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR-ANON-KEY-HERE

# API Configuration
VITE_API_URL=http://localhost:8000

# Environment
VITE_APP_ENV=development
```

**⚠️ Important:** Frontend uses `VITE_` prefix for all variables!

---

## ✅ Verification

After creating both .env files, run:

```bash
cd ~/projects/jovey
./verify-setup.sh
```

This will check if your .env files are configured correctly!

---

## 🗄️ Next: Run Database Schema

Once .env files are created, you need to set up the database tables.

### Option 1: Via Supabase Dashboard (Easiest)

1. Go to your **jovey** project dashboard
2. Click **SQL Editor** (left sidebar)
3. Click **"New query"**
4. Copy the ENTIRE contents of: `backend/database/schema.sql`
5. Paste it into the SQL editor
6. Click **"Run"** or press `Ctrl+Enter`
7. You should see: "Success. No rows returned"

### Option 2: Via Command Line (Alternative)

```bash
# If you have Supabase CLI installed
cd ~/projects/jovey/backend/database
supabase db push
```

### Verify Tables Created

1. Go to **Table Editor** (left sidebar)
2. You should see these tables:
   - ✅ events
   - ✅ user_profiles
   - ✅ products
   - ✅ dealer_product_pricing

---

## 🚀 Ready to Start!

Once you have:
- ✅ Backend .env file created
- ✅ Frontend .env file created
- ✅ Database schema run in Supabase
- ✅ Tables visible in Supabase dashboard

You're ready to start the applications!

### Start Backend
```bash
cd ~/projects/jovey/backend
conda activate jovey
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd ~/projects/jovey/frontend
npm run dev
```

### Test
- Backend: http://localhost:8000
- Backend Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

---

## 🐛 Troubleshooting

**Problem: Can't find Anthropic API key**
```bash
# Check if it's in .bashrc
cat ~/.bashrc | grep ANTHROPIC

# If not there, you'll need to add it:
# 1. Get your key from: https://console.anthropic.com/
# 2. Add to .bashrc: export ANTHROPIC_API_KEY="your-key-here"
# 3. Reload: source ~/.bashrc
```

**Problem: JWT_SECRET - what should I use?**
```bash
# Generate a random secret:
openssl rand -base64 32

# Copy the output and paste it as JWT_SECRET value
```

**Problem: Supabase keys not working**
- Double-check you copied the ENTIRE key (they're very long!)
- Make sure no extra spaces at beginning or end
- Verify the project is "jovey" (not a different project)

---

**Questions?** Check `SETUP-INSTRUCTIONS.md` for more details!
