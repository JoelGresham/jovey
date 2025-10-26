#!/bin/bash
# Jovey Backend Setup Script

echo "🚀 Setting up Jovey Backend..."

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Conda first."
    exit 1
fi

# Create conda environment
echo "📦 Creating conda environment 'jovey'..."
conda create -n jovey python=3.11 -y

# Activate environment
echo "🔄 Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate jovey

# Install dependencies
echo "📥 Installing Python packages..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual credentials!"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your Supabase credentials"
echo "2. Run: conda activate jovey"
echo "3. Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "4. Visit: http://localhost:8000/docs"
