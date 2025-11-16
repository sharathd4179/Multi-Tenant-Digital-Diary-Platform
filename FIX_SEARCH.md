# How to Fix Semantic Search

## Problem
Search returns "No relevant notes found" because FAISS indexes don't exist.

## Solution

### Step 1: Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign up/login and create an API key
3. Copy the key (starts with `sk-`)

### Step 2: Update .env File
Edit `.env` file and set:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Restart Backend
```bash
cd infra
docker-compose restart backend
```

### Step 4: Build FAISS Indexes
```bash
# Make sure you have notes in the database first!
docker-compose exec backend python /app/build_indexes_docker.py
```

### Step 5: Test Search
1. Go to http://localhost:8501
2. Navigate to "Search" page
3. Enter a query like "tell me about my notes"
4. You should see results!

## Alternative: Basic Search Without OpenAI

If you don't want to use OpenAI, you can still search notes via the API using keyword matching, but you won't get:
- Semantic search (understanding meaning)
- AI summarization
- Task extraction

The basic `/notes/` endpoint supports filtering by tags and date ranges.

## Troubleshooting

### "OPENAI_API_KEY not configured"
- Make sure you set it in `.env` file
- Restart the backend container
- Check: `docker-compose exec backend env | grep OPENAI`

### "Index for tenant not found"
- Run the build_indexes_docker.py script
- Make sure you have notes in the database
- Check that indexes were created: `docker-compose exec backend ls -la /app/vector_indexes/`

### "No relevant notes found"
- Make sure you have notes with content
- Rebuild indexes after adding new notes
- Check that your query matches content in your notes



