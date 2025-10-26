# Jovey Quick Start Guide
## Get Up and Running in 15 Minutes

**Last Updated:** 2025-10-26
**For Developer:** gresh on WSL2 Ubuntu

---

## 🚀 Ready to Start Coding?

All planning is complete! Follow these steps to begin development.

---

## Phase 0: Project Setup (Do This First)

### Step 1: Create Supabase Projects (5 minutes)

```bash
# 1. Go to https://supabase.com and sign in
# 2. Click "New Project"
# 3. Create development project:
#    - Name: jovey
#    - Database Password: (save this securely!)
#    - Region: Choose closest to you
#    - Wait for project to be created (~2 minutes)
#
# 4. Get your credentials:
#    - Go to Project Settings > API
#    - Copy "Project URL" (SUPABASE_URL)
#    - Copy "anon public" key (SUPABASE_KEY)
#    - Copy "service_role" key (SUPABASE_SERVICE_KEY)
```

### Step 2: Initialize Backend (5 minutes)

```bash
# Navigate to project
cd ~/projects/jovey

# Create backend directory
mkdir backend
cd backend

# Create conda environment
conda create -n jovey python=3.11 -y
conda activate jovey

# Install dependencies
pip install fastapi[all] uvicorn[standard] supabase anthropic python-dotenv pydantic pydantic-settings httpx

# Create project structure
mkdir -p app/{core,functions,agents,tests}
touch app/__init__.py

# Create main.py
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Jovey API",
    description="AI-Native Business Operating System",
    version="0.1.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Jovey API", "status": "online"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
EOF

# Create .env file
cat > .env << 'EOF'
# Supabase
SUPABASE_URL=your-project-url-here
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here

# Claude API (already configured in ~/.bashrc)
ANTHROPIC_API_KEY=your-key-here

# Application
APP_ENV=development
JWT_SECRET=change-this-to-random-secret
EOF

# Create .env.example (for Git)
cat > .env.example << 'EOF'
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_KEY=
ANTHROPIC_API_KEY=
APP_ENV=development
JWT_SECRET=
EOF

# Save requirements
pip freeze > requirements.txt

# Test backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Open browser to http://localhost:8000
# You should see: {"message": "Jovey API", "status": "online"}
# Also check http://localhost:8000/docs for auto-generated API docs
# Press Ctrl+C to stop
```

### Step 3: Initialize Frontend (5 minutes)

```bash
# Open new terminal, navigate to project
cd ~/projects/jovey

# Create React app with Vite
npm create vite@latest frontend -- --template react
cd frontend

# Install dependencies
npm install

# Install Jovey-specific packages
npm install @supabase/supabase-js @tanstack/react-query zustand react-router-dom

# Install UI/styling
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install shadcn-ui (optional but recommended)
npx shadcn-ui@latest init

# Create Supabase client config
mkdir -p src/config
cat > src/config/supabase.js << 'EOF'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
EOF

# Create .env file
cat > .env << 'EOF'
VITE_SUPABASE_URL=your-project-url-here
VITE_SUPABASE_ANON_KEY=your-anon-key-here
VITE_API_URL=http://localhost:8000
EOF

# Create .env.example
cat > .env.example << 'EOF'
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_URL=http://localhost:8000
EOF

# Test frontend
npm run dev

# Open browser to http://localhost:3000
# You should see the Vite + React welcome page
# Press Ctrl+C to stop
```

### Step 4: Initialize Git Repository

```bash
cd ~/projects/jovey

# Initialize Git (if not already done)
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Jupyter
.ipynb_checkpoints/

# Logs
*.log
logs/
EOF

# Initial commit
git add .
git commit -m "Initial commit: Jovey project setup"

# Connect to GitHub (optional, do when ready)
# git remote add origin https://github.com/gresh/jovey.git
# git branch -M main
# git push -u origin main
```

---

## ✅ Verification Checklist

After completing Phase 0 setup, verify:

- [ ] Supabase project created and credentials saved
- [ ] Backend running at http://localhost:8000
- [ ] Backend docs accessible at http://localhost:8000/docs
- [ ] Frontend running at http://localhost:3000
- [ ] Conda environment "jovey" activated
- [ ] Git repository initialized
- [ ] .env files created (not committed to Git)
- [ ] Can access backend from frontend (CORS working)

---

## 🎯 What's Next? (Phase 1: Week 2-3)

Once Phase 0 is complete, start building core infrastructure:

### Week 2: Event Store & Database Manager

**Backend Tasks:**
1. Create database schema in Supabase
2. Build event store interface
3. Create Database Manager function
4. Test event posting and processing

**Frontend Tasks:**
1. Build authentication pages (login/register)
2. Create Database Manager UI (event stream viewer)
3. Test authentication flow

### Week 3: Base Agent Architecture

**Backend Tasks:**
1. Create BaseAgent class with Claude integration
2. Build agent communication framework
3. Test agent posting events

**Frontend Tasks:**
1. Create agent decision approval UI
2. Build real-time event stream display
3. Test agent-human collaboration

---

## 📚 Reference During Development

### Daily Commands

```bash
# Activate environment
conda activate jovey

# Start backend (Terminal 1)
cd ~/projects/jovey/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (Terminal 2)
cd ~/projects/jovey/frontend
npm run dev

# Git workflow
git status
git add .
git commit -m "Descriptive message"
git push
```

### Key URLs

- **Backend API:** http://localhost:8000
- **Backend Docs:** http://localhost:8000/docs (auto-generated by FastAPI)
- **Frontend:** http://localhost:3000
- **Supabase Dashboard:** https://supabase.com/dashboard

### Important Files

- **Backend entry:** `backend/app/main.py`
- **Frontend entry:** `frontend/src/main.jsx`
- **Backend env:** `backend/.env`
- **Frontend env:** `frontend/.env`
- **Backend config:** `backend/app/config.py` (create as needed)
- **Frontend Supabase:** `frontend/src/config/supabase.js`

### Documentation

When stuck, refer to:
1. **This guide** - Quick start and daily commands
2. **project-status.md** - Current status and what's next
3. **technical-architecture.md** - Detailed technical design
4. **development-setup.md** - Your machine configuration
5. **business-context.md** - Jovey business requirements

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend can't reach backend

```bash
# Verify CORS in backend/app/main.py
# Ensure backend bound to 0.0.0.0, not 127.0.0.1
# Check .env has correct VITE_API_URL
```

### Conda environment issues

```bash
# Reinitialize conda
conda init bash
source ~/.bashrc
conda activate jovey
```

### Supabase connection errors

```bash
# Verify .env has correct credentials
# Check Supabase project is running (not paused)
# Test connection in Python:
python -c "from supabase import create_client; client = create_client('URL', 'KEY'); print('Connected!')"
```

---

## 💡 Pro Tips

1. **Keep two terminals open:** One for backend, one for frontend
2. **Use VS Code:** Open entire jovey folder in VS Code
3. **Auto-reload works:** FastAPI and Vite both hot-reload on file changes
4. **Check API docs:** FastAPI auto-generates docs at /docs endpoint
5. **Use Thunder Client:** VS Code extension for testing API endpoints
6. **Git commit often:** Small, frequent commits are better
7. **Document as you go:** Update docs when making decisions

---

## 🎉 You're Ready!

After completing Phase 0 setup, you'll have:
- ✅ Working backend API (FastAPI)
- ✅ Working frontend (React)
- ✅ Supabase database connected
- ✅ Development environment configured
- ✅ Git repository initialized

**Next session:** Start building the event store and Database Manager function!

---

**Questions?** Check the documentation in `/docs/` folder:
- Technical questions → technical-architecture.md
- Setup questions → development-setup.md
- Status questions → project-status.md
- Business questions → business-context.md
