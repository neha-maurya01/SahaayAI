#!/bin/bash

# SahaayAI Installation Script
# This script sets up the project and installs all dependencies

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              SahaayAI Installation Script                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Found Python $PYTHON_VERSION${NC}"

# Check if virtual environment exists
if [ ! -d "sahaayAI" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv sahaayAI
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source sahaayAI/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✅ pip upgraded${NC}"

# Install dependencies
echo ""
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt
echo -e "${GREEN}✅ All dependencies installed${NC}"

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p storage/audio
mkdir -p logs
mkdir -p data/knowledge_base
mkdir -p data/prompts
echo -e "${GREEN}✅ Directories created${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  .env file created. You need to add your API keys!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  IMPORTANT: Configure your API keys in .env file"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Get your Gemini API key:"
    echo "   Visit: https://makersuite.google.com/app/apikey"
    echo "   Sign in with Google account"
    echo "   Click 'Create API Key'"
    echo "   Copy the key"
    echo ""
    echo "2. Generate secret keys:"
    echo "   SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")"
    echo "   ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")"
    echo ""
    echo "3. Edit .env file and add:"
    echo "   GEMINI_API_KEY=your_key_here"
    echo "   SECRET_KEY=generated_secret_key"
    echo "   ENCRYPTION_KEY=generated_encryption_key"
    echo ""
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from app.database import init_db; init_db()" 2>/dev/null || echo -e "${YELLOW}⚠️  Database will be initialized on first run${NC}"
echo -e "${GREEN}✅ Database ready${NC}"

# Installation complete
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Installation Complete! 🎉                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your API keys (if not done):"
echo "   nano .env"
echo ""
echo "2. Run the demo script:"
echo "   python3 demo.py"
echo ""
echo "3. Start the API server:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Visit the API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. Read the documentation:"
echo "   - SETUP.md - Quick start guide"
echo "   - ARCHITECTURE.md - Technical details"
echo "   - README.md - Project overview"
echo ""
echo "For detailed instructions, see SETUP.md"
echo ""
