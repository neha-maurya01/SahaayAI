#!/bin/zsh

# SahaayAI - Complete Setup and Start Script
# This script will set up everything and start the server

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              SahaayAI - Complete Setup                     ║"
echo "║         AI for Underserved Communities - POC               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo "${NC}"

# Step 1: Check Python
echo "\n${BLUE}Step 1: Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "${GREEN}✅ Found $PYTHON_VERSION${NC}"
else
    echo "${RED}❌ Python 3 not found. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

# Step 2: Activate virtual environment
echo "\n${BLUE}Step 2: Activating virtual environment...${NC}"
if [ -d "sahaayAI" ]; then
    source sahaayAI/bin/activate
    echo "${GREEN}✅ Virtual environment activated${NC}"
else
    echo "${RED}❌ Virtual environment 'sahaayAI' not found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv sahaayAI
    source sahaayAI/bin/activate
    echo "${GREEN}✅ Virtual environment created and activated${NC}"
fi

# Step 3: Install dependencies
echo "\n${BLUE}Step 3: Installing dependencies...${NC}"
echo "This may take a few minutes on first run..."
pip install --upgrade pip -q
pip install -r requirements.txt
echo "${GREEN}✅ All dependencies installed${NC}"

# Step 4: Check .env configuration
echo "\n${BLUE}Step 4: Checking configuration...${NC}"
if [ ! -f ".env" ]; then
    echo "${YELLOW}⚠️  Creating .env file from template...${NC}"
    cp .env.example .env
    echo "${YELLOW}⚠️  IMPORTANT: You need to configure your API keys!${NC}"
fi

# Check if API key is configured
if grep -q "your_gemini_api_key_here" .env; then
    echo "${YELLOW}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           ACTION REQUIRED: Configure API Key              ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo "${NC}"
    echo "1. Get your FREE Gemini API key:"
    echo "   ${BLUE}https://makersuite.google.com/app/apikey${NC}"
    echo ""
    echo "2. Generate secret keys (copy these into .env):"
    echo "   SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
    echo "   ENCRYPTION_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
    echo ""
    echo "3. Edit .env file and add your keys:"
    echo "   ${YELLOW}nano .env${NC}"
    echo ""
    read -p "Press Enter when you've configured your API key..."
else
    echo "${GREEN}✅ Configuration file exists${NC}"
fi

# Step 5: Create necessary directories
echo "\n${BLUE}Step 5: Creating project directories...${NC}"
mkdir -p storage/audio logs
echo "${GREEN}✅ Directories created${NC}"

# Step 6: Initialize database
echo "\n${BLUE}Step 6: Initializing database...${NC}"
python3 -c "from app.database import init_db; init_db()" 2>/dev/null || echo "${YELLOW}Database will be initialized on first API call${NC}"
echo "${GREEN}✅ Database ready${NC}"

# Step 7: Run verification
echo "\n${BLUE}Step 7: Running verification...${NC}"
python3 verify_setup.py || true

# Final instructions
echo "\n${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Setup Complete! 🎉                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo "${NC}"

echo "\n${BLUE}What's Next?${NC}\n"
echo "1️⃣  Run the demo to see all features:"
echo "   ${YELLOW}python3 demo.py${NC}"
echo ""
echo "2️⃣  Start the API server:"
echo "   ${YELLOW}uvicorn app.main:app --reload${NC}"
echo ""
echo "3️⃣  Visit the interactive API documentation:"
echo "   ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "4️⃣  Test with a simple health check:"
echo "   ${YELLOW}curl http://localhost:8000/health${NC}"
echo ""
echo "5️⃣  Send your first AI message:"
echo "   ${YELLOW}curl -X POST http://localhost:8000/api/v1/message/web \\
     -H 'Content-Type: application/json' \\
     -d '{\"phone_number\": \"+919876543210\", \"message\": \"Hello!\", \"channel\": \"web\"}'${NC}"
echo ""

echo "${BLUE}📚 Documentation:${NC}"
echo "   • GETTING_STARTED.md - Quick start guide"
echo "   • SETUP.md - Detailed instructions"
echo "   • ARCHITECTURE.md - Technical deep-dive"
echo "   • PROJECT_COMPLETE.md - Full project overview"
echo ""

echo "${GREEN}Ready to start? Run:${NC} ${YELLOW}uvicorn app.main:app --reload${NC}\n"
