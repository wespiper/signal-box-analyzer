#!/bin/bash

# Signal Box Analyzer Startup Script

echo "🚀 Starting Signal Box Cost Analyzer"
echo "=================================="

# Check if Signal Box is installed
echo "📦 Checking Signal Box dependency..."
python -c "import signal_box; print('✅ Signal Box core is available')" 2>/dev/null || {
    echo "⚠️  Signal Box core not found. Installing..."
    pip install git+https://github.com/wespiper/signal-box.git
}

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create reports directory
mkdir -p reports

echo ""
echo "🎯 Ready to start! Run these commands in separate terminals:"
echo ""
echo "Backend:  python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo "Frontend: cd frontend && npm run dev"
echo ""
echo "Then open: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "✨ Happy analyzing!"