#!/bin/bash
# Script to build FAISS indexes for semantic search
# This requires OpenAI API key and notes in the database

echo "Building FAISS indexes for semantic search..."
echo ""

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set. Semantic search will not work."
    echo "   Set it in your .env file or export it:"
    echo "   export OPENAI_API_KEY=your-key-here"
    echo ""
fi

# Database URL (adjust if needed)
DB_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/diarydb}"

# Run the index creation script
python scripts/create_faiss_index.py \
    --db-url="$DB_URL" \
    --openai-api-key="${OPENAI_API_KEY:-}"

echo ""
echo "✅ Index building complete!"
echo "   Indexes are saved in: vector_indexes/"
echo ""
echo "⚠️  Note: If running in Docker, you need to:"
echo "   1. Copy indexes to the backend container, OR"
echo "   2. Mount vector_indexes/ as a volume in docker-compose.yml"



