#!/bin/bash
# KI-QMS Backend Restart Script
# Stoppt alle laufenden Backend-Prozesse und startet neu

echo "🛑 Stopping existing backend processes..."
pkill -f "uvicorn.*app.main:app" || true
sleep 2

echo "🚀 Starting backend..."
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo "✅ Backend started on http://localhost:8000" 