#!/bin/bash

# Ensure virtual environment is used
VENV_PATH="./.venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "Virtual environment not found. Please create one and install requirements."
    exit 1
fi

echo "🚀 Lancement du Backend FastAPI..."
$VENV_PATH/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be available
echo "⏳ Attente du démarrage du Backend..."
BACKEND_URL="http://localhost:8000"
MAX_RETRIES=30
RETRY_COUNT=0
until curl -s -f "$BACKEND_URL" > /dev/null || [ $RETRY_COUNT -ge $MAX_RETRIES ]; do
    echo "Backend non disponible, nouvelle tentative dans 2 secondes..."
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "❌ Le Backend n'a pas démarré après plusieurs tentatives. Arrêt."
    kill $BACKEND_PID
    exit 1
fi
echo "✅ Backend démarré et disponible."

echo "🎨 Lancement du Frontend Streamlit..."
$VENV_PATH/bin/streamlit run frontend/main.py --server.port 8501 &
FRONTEND_PID=$!

echo "✅ Application démarrée !"
echo "API : http://localhost:8000"
echo "Interface : http://localhost:8501"

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID; echo 'Arrêt des services...'; exit" INT TERM
wait
