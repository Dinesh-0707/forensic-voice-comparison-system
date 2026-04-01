#!/bin/bash

echo "Activating virtual environment..."
source venv/bin/activate

echo "Running Flask App..."
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
