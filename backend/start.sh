#!/bin/bash
echo "Running ingestion to build ChromaDB..."
cd /app
python ingest.py
echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8080