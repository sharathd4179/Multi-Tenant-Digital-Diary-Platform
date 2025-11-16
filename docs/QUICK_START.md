# ⚡ Quick Start Guide

Get your Multi-Tenant Diary Assistant running in 5 minutes!

## Prerequisites

- Docker and Docker Compose
- OpenAI API key (optional, for RAG features)
- Git (for deployment)

## Local Setup

### 1. Create Environment File

Create `.env` in project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/diarydb
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your_minimum_32_character_secret_key_here
OPENAI_API_KEY=sk-your-openai-api-key-here
ENVIRONMENT=development
```

### 2. Start Services

```bash
cd infra
docker-compose up --build
```

### 3. Access Application

- **Frontend:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health/

## First Steps

1. **Create a Tenant:**
   - Go to http://localhost:8000/docs
   - Use `/auth/register-tenant` endpoint
   - Save your `tenant_id`

2. **Login:**
   - Go to http://localhost:8501
   - Enter tenant_id, username, password

3. **Create Notes:**
   - Use the Diary section
   - Add tags for organization

4. **Search:**
   - Use semantic search (requires FAISS indexes)
   - Build indexes: `python scripts/create_faiss_index.py`

## Next Steps

- See [Setup Guide](SETUP.md) for detailed configuration
- See [Usage Guide](../USAGE_GUIDE.md) for features
- See [Deployment Guide](DEPLOYMENT.md) for production

