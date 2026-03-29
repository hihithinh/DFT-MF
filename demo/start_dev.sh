#!/bin/bash

# DFT-MF Development Server Startup Script

echo "🚀 Starting DFT-MF Development Servers..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "📚 Installing Node.js dependencies..."
npm install

# Start backend server
echo "🔧 Starting backend server..."
cd server && python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend development server
echo "🎨 Starting frontend development server..."
cd .. && npm run dev &
FRONTEND_PID=$!

echo "✅ Servers started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8080"
echo "📊 Health Check: http://localhost:8080/health"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All servers stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait for processes
wait
