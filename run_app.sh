#!/bin/bash

PROJECT_DIR="./"
VENV_DIR="$PROJECT_DIR/.venv"

cd "$PROJECT_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

source "$VENV_DIR/bin/activate"

gunicorn -w 4 app:app
