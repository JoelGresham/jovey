# Jovey Development Environment Setup
## Local Development Machine Configuration

**Last Updated:** 2025-10-25
**Developer:** gresh

---

## Hardware Specifications

**Machine:** Lenovo Legion Pro 7i laptop

| Component | Specification |
|-----------|---------------|
| **CPU** | Intel Core Ultra 9 275HX |
| **GPU** | NVIDIA GeForce RTX 5070 Ti Laptop (12GB VRAM) |
| **RAM** | 64GB DDR5 |
| **Storage** | 1TB SSD |
| **CUDA** | 12.8 (fully working) |

**Notes:**
- GPU acceleration verified working for AI workloads
- Excellent specs for local AI development and testing
- More than sufficient for running local AI models if needed

---

## Operating System & Environment

### Primary Development Environment

**OS:** WSL2 (Ubuntu on Windows)
- Developer prefers Linux environment over Windows
- All development happens in WSL unless specified otherwise

**Terminal:** Windows Terminal with PowerShell

**File System Structure:**
```
~/projects/                          # All projects stored here
  └── jovey/                        # This project
      ├── docs/                     # Documentation
      ├── backend/                  # FastAPI backend (to be created)
      ├── frontend/                 # React frontend (to be created)
      └── ...

# Access from Windows:
\\wsl$\Ubuntu\home\gresh\projects\jovey
```

---

## Development Tools

### Core Tools

| Tool | Purpose | Status |
|------|---------|--------|
| **Conda** | Python environment manager | ✅ Installed |
| **Python** | Primary language | ✅ 3.11 (ai-dev environment) |
| **VS Code** | Code editor | ✅ Installed |
| **Git** | Version control | ✅ Installed |
| **Docker** | Containerization | ✅ Installed |
| **Jupyter Notebook** | Interactive development | ✅ Installed |

### Conda Environment

**Primary Environment:** `ai-dev`
- Python 3.11
- Used for AI/ML development

**For Jovey Project:**
Will likely create dedicated conda environment:
```bash
conda create -n jovey python=3.11
conda activate jovey
```

---

## AI/ML Stack (Already Installed)

### Core AI Libraries

| Library | Version | Notes |
|---------|---------|-------|
| **PyTorch** | 2.10+ | Nightly build for RTX 50-series, CUDA 12.8 support |
| **Claude Agent SDK** | Latest | Python SDK for Claude |
| **Transformers** | Latest | Hugging Face transformers |
| **pandas** | Latest | Data manipulation |
| **numpy** | Latest | Numerical computing |
| **matplotlib** | Latest | Visualization |
| **scikit-learn** | Latest | ML utilities |
| **python-dotenv** | Latest | Environment variable management |

### Jovey-Specific Dependencies (To Install)

```bash
# FastAPI and dependencies
pip install fastapi[all]
pip install uvicorn[standard]
pip install pydantic
pip install pydantic-settings

# Supabase
pip install supabase

# Claude API (if not using Agent SDK)
pip install anthropic

# Additional utilities
pip install python-dotenv
pip install httpx
pip install python-multipart
pip install python-jose[cryptography]
pip install passlib[bcrypt]
```

---

## API Keys & Authentication

### Current API Access

| Service | Status | Storage Location |
|---------|--------|------------------|
| **Anthropic API (Claude)** | ✅ Authenticated & working | `~/.bashrc` |
| **OpenAI API** | ✅ Available | `~/.bashrc` |
| **Google Gemini API** | ✅ Available | `~/.bashrc` |
| **Stable Diffusion API** | ✅ Available | `~/.bashrc` |

### For Jovey Project

**Environment Variables Needed:**
```bash
# Add to ~/.bashrc or project-specific .env file

# Supabase
export SUPABASE_URL="your-project-url"
export SUPABASE_KEY="your-anon-key"
export SUPABASE_SERVICE_KEY="your-service-key"

# Claude API (already configured)
export ANTHROPIC_API_KEY="your-key-here"

# Application secrets
export JWT_SECRET="generate-random-secret"
export APP_ENV="development"
```

**Recommendation for Jovey:**
Create project-specific `.env` file (not committed to Git):
```bash
# /home/gresh/projects/jovey/backend/.env
SUPABASE_URL=...
SUPABASE_KEY=...
ANTHROPIC_API_KEY=...
```

---

## Infrastructure & Services

### Currently Available

| Service | Type | Status | Notes |
|---------|------|--------|-------|
| **n8n** | Workflow automation | ✅ Local Docker instance | Could be useful for integrations |
| **Supabase** | Database/Auth | ✅ Account exists | Primary database for Jovey |
| **GitHub** | Code repository | ✅ Active | For Jovey version control |
| **Replit** | Web hosting | ✅ Available | Alternative hosting option |
| **ComfyUI** | Image/video generation | ✅ Installed | Not needed for Jovey Phase 1 |

### For Jovey Hosting (Future)

**Development:**
- Backend: `localhost:8000` (FastAPI via uvicorn)
- Frontend: `localhost:3000` (React via Vite/CRA)
- Database: Supabase cloud (development project)

**Production (when ready):**
- Backend: DigitalOcean/Render/Railway
- Frontend: Vercel/Netlify
- Database: Supabase cloud (production project)

---

## Project-Specific Setup for Jovey

### Phase 0 Setup Checklist

**Step 1: Create Supabase Projects**
```bash
# Via Supabase dashboard (https://supabase.com)
1. Create "jovey" project (for development)
2. Create "jovey-staging" project (for staging, optional - future)
3. Save credentials to .env file
```

**Step 2: Initialize Backend**
```bash
cd ~/projects/jovey
mkdir backend
cd backend

# Create conda environment
conda create -n jovey python=3.11
conda activate jovey

# Initialize Python project
pip install fastapi[all] uvicorn[standard] supabase anthropic python-dotenv

# Create project structure
mkdir -p app/{core,functions,agents,tests}
touch app/__init__.py
touch app/main.py
touch .env
touch .env.example
touch requirements.txt

# Save installed packages
pip freeze > requirements.txt
```

**Step 3: Initialize Frontend**
```bash
cd ~/projects/jovey

# Using Vite (recommended for React)
npm create vite@latest frontend -- --template react
cd frontend
npm install

# Install Jovey dependencies
npm install @supabase/supabase-js
npm install @tanstack/react-query
npm install zustand
npm install react-router-dom
npm install tailwindcss postcss autoprefixer
npm install @anthropic-ai/sdk  # if needed for frontend

# Initialize Tailwind
npx tailwindcss init -p
```

**Step 4: Initialize Git Repository**
```bash
cd ~/projects/jovey

# If not already initialized
git init
git add .
git commit -m "Initial commit: Jovey AI-native business OS"

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

# Connect to GitHub (when ready)
# git remote add origin https://github.com/gresh/jovey.git
# git push -u origin main
```

---

## Development Workflow

### Starting Development Session

```bash
# 1. Navigate to project
cd ~/projects/jovey

# 2. Activate conda environment
conda activate jovey

# 3. Start backend (in one terminal)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Start frontend (in another terminal)
cd frontend
npm run dev

# 5. Access applications
# Backend API: http://localhost:8000
# Backend docs: http://localhost:8000/docs (FastAPI auto-generated)
# Frontend: http://localhost:3000
```

### Working with Jupyter (if needed)

```bash
conda activate jovey
jupyter notebook --no-browser --port=8888

# Access via browser at localhost:8888
```

### Docker (if containerizing)

```bash
# Backend Dockerfile example
cd ~/projects/jovey/backend
docker build -t jovey-backend .
docker run -p 8000:8000 --env-file .env jovey-backend

# Frontend Dockerfile example
cd ~/projects/jovey/frontend
docker build -t jovey-frontend .
docker run -p 3000:3000 jovey-frontend
```

---

## IDE Configuration

### VS Code Setup for Jovey

**Recommended Extensions:**
```
- Python (Microsoft)
- Pylance
- Python Debugger
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- ESLint
- Prettier
- GitLens
- Docker
- Thunder Client (for API testing)
```

**VS Code Settings (`.vscode/settings.json`):**
```json
{
  "python.defaultInterpreterPath": "/home/gresh/miniconda3/envs/jovey/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

---

## Performance Optimizations

### Leveraging GPU for Development (Optional)

While Jovey doesn't require GPU for core functionality, if we add any ML features:

```python
# Check PyTorch GPU availability
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

# Output (on this machine):
# CUDA available: True
# CUDA version: 12.8
# GPU: NVIDIA GeForce RTX 5070 Ti Laptop GPU
```

**Use Cases for GPU:**
- Local LLM inference (if we add local models)
- Batch processing of AI decisions
- Training custom models for specific functions

---

## Backup & Version Control

### Git Strategy

```bash
# Daily workflow
git add .
git commit -m "Descriptive message"
git push origin main

# Feature branches for major changes
git checkout -b feature/category-management-agent
# ... work on feature ...
git commit -m "Implement category management agent"
git push origin feature/category-management-agent
# ... create PR on GitHub ...
```

### Backup Strategy

**Important files:**
- Source code: Git (GitHub)
- Documentation: Git (GitHub)
- Database: Supabase automated backups
- Environment config: Manual backup to OneDrive

**OneDrive backup (for critical configs):**
```bash
# Periodically backup .env.example and docs
cp ~/projects/jovey/.env.example ~/OneDrive/backups/jovey/
cp -r ~/projects/jovey/docs ~/OneDrive/backups/jovey/
```

---

## Testing Setup

### Backend Testing

```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run tests
cd ~/projects/jovey/backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

### Frontend Testing

```bash
# Install testing dependencies
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom

# Run tests
cd ~/projects/jovey/frontend
npm run test
```

---

## Troubleshooting

### Common Issues

**Issue: Conda environment not activating**
```bash
# Initialize conda for bash
conda init bash
source ~/.bashrc
conda activate jovey
```

**Issue: Port already in use**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
```

**Issue: Cannot access localhost from Windows browser**
```bash
# Ensure WSL port forwarding is working
# FastAPI should bind to 0.0.0.0, not 127.0.0.1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access from Windows: http://localhost:8000
```

**Issue: GPU not recognized in PyTorch**
```bash
# Already working, but if issues arise:
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
```

---

## Development Preferences

**Key Notes from Developer:**
- Prefer Linux/WSL environment over Windows
- Prefer practical, production-ready solutions
- Building AI-led business applications
- Conda for Python environment management
- VS Code as primary editor
- Git for all version control

**For Jovey Specifically:**
- FastAPI backend (Python 3.11)
- React frontend
- Supabase for database
- Claude API for AI agents
- Development in WSL2 Ubuntu
- Deploy to simple hosting initially (Replit/DigitalOcean/Render)

---

## Quick Reference Commands

### Daily Development
```bash
# Start session
cd ~/projects/jovey
conda activate jovey

# Backend
cd backend && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev

# Git
git status
git add . && git commit -m "message" && git push
```

### Database (Supabase)
```bash
# Via Supabase CLI (if installed)
supabase start           # Local development
supabase db push         # Push schema changes
supabase gen types python # Generate Python types
```

### Package Management
```bash
# Backend
pip install <package>
pip freeze > requirements.txt

# Frontend
npm install <package>
npm install                 # Install from package.json
```

---

## Next Steps for Phase 0

**Ready to begin development with this setup:**

1. ✅ Hardware capable (GPU not needed but available)
2. ✅ WSL2 environment ready
3. ✅ Python 3.11 with Conda available
4. ✅ VS Code installed
5. ✅ Git installed
6. ✅ Docker available
7. ✅ Anthropic API authenticated
8. ✅ Supabase account exists

**To Start Phase 0 (Week 1):**
1. Create Supabase project
2. Initialize backend with FastAPI
3. Initialize frontend with React + Vite
4. Set up Git repository
5. Create database schema
6. Build basic auth flow

---

**Document Version:** 1.0
**Date:** 2025-10-25
**Developer:** gresh
**Machine:** Lenovo Legion Pro 7i (WSL2 Ubuntu)
