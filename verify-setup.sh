#!/bin/bash
# Jovey Setup Verification Script
# Checks if everything is ready to run

echo "🔍 Verifying Jovey Setup..."
echo ""

# Color codes
GREEN='\033[0.32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check functions
check_exists() {
    if [ -f "$1" ] || [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        return 1
    fi
}

check_env_var() {
    if grep -q "$1=" "$2" 2>/dev/null; then
        value=$(grep "$1=" "$2" | cut -d '=' -f2)
        if [ ! -z "$value" ] && [ "$value" != "your-"* ] && [ "$value" != "https://your-"* ]; then
            echo -e "${GREEN}✓${NC} $1 configured"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} $1 needs to be set"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} $1 missing from $2"
        return 1
    fi
}

errors=0

# Check backend
echo "Backend:"
check_exists "backend/app/main.py" "FastAPI app exists" || ((errors++))
check_exists "backend/requirements.txt" "Requirements file exists" || ((errors++))
check_exists "backend/.env.example" "Environment template exists" || ((errors++))
check_exists "backend/database/schema.sql" "Database schema exists" || ((errors++))

if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    echo "  Checking configuration..."
    check_env_var "SUPABASE_URL" "backend/.env" || ((errors++))
    check_env_var "SUPABASE_KEY" "backend/.env" || ((errors++))
    check_env_var "ANTHROPIC_API_KEY" "backend/.env" || ((errors++))
    check_env_var "JWT_SECRET" "backend/.env" || ((errors++))
else
    echo -e "${YELLOW}⚠${NC} backend/.env file missing - need to create"
    ((errors++))
fi

echo ""

# Check frontend
echo "Frontend:"
check_exists "frontend/package.json" "Package.json exists" || ((errors++))
check_exists "frontend/src/config/supabase.js" "Supabase config exists" || ((errors++))
check_exists "frontend/.env.example" "Environment template exists" || ((errors++))
check_exists "frontend/node_modules" "Dependencies installed" || ((errors++))

if [ -f "frontend/.env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    echo "  Checking configuration..."
    check_env_var "VITE_SUPABASE_URL" "frontend/.env" || ((errors++))
    check_env_var "VITE_SUPABASE_ANON_KEY" "frontend/.env" || ((errors++))
    check_env_var "VITE_API_URL" "frontend/.env" || ((errors++))
else
    echo -e "${YELLOW}⚠${NC} frontend/.env file missing - need to create"
    ((errors++))
fi

echo ""

# Check conda environment
echo "Python Environment:"
if conda env list | grep -q "jovey"; then
    echo -e "${GREEN}✓${NC} Conda environment 'jovey' exists"
else
    echo -e "${YELLOW}⚠${NC} Conda environment 'jovey' not created yet"
    ((errors++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✅ Setup verification passed!${NC}"
    echo ""
    echo "Ready to start:"
    echo "1. Backend: cd backend && conda activate jovey && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo "2. Frontend: cd frontend && npm run dev"
    exit 0
else
    echo -e "${YELLOW}⚠️  Found $errors issue(s)${NC}"
    echo ""
    echo "Next steps:"
    if [ ! -f "backend/.env" ]; then
        echo "- Create backend/.env (copy from .env.example)"
    fi
    if [ ! -f "frontend/.env" ]; then
        echo "- Create frontend/.env (copy from .env.example)"
    fi
    echo "- Follow SETUP-INSTRUCTIONS.md for complete guide"
    exit 1
fi
