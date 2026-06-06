#!/bin/bash
echo "Checking if ChromaDB needs initialization..."
cd /app

python -c "
import chromadb, sys
client = chromadb.PersistentClient(path='/app/chroma_db')
try:
    col = client.get_collection('shahid_knowledge_base')
    count = col.count()
    if count > 0:
        print(f'Database already has {count} documents. Skipping ingestion.')
        sys.exit(0)
    else:
        print('Database empty. Running ingestion...')
        sys.exit(1)
except:
    print('Collection not found. Running ingestion...')
    sys.exit(1)
"

if [ $? -eq 1 ]; then
    echo "Running ingestion..."
    python ingest.py
else
    echo "Skipping ingestion."
fi

echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8080