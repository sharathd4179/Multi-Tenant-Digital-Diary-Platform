# 🔧 Complete Setup Guide

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git
cd Multi-Tenant-Digital-Diary-Platform
```

### 2. Environment Configuration

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/diarydb

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your_minimum_32_character_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (for RAG features)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Application
ENVIRONMENT=development
LOG_LEVEL=info
```

### 3. Install Dependencies

**For Development:**
```bash
pip install -r requirements-dev.txt
```

**For Production:**
```bash
pip install -r requirements.txt
```

### 4. Start with Docker

```bash
cd infra
docker-compose up --build
```

## GitHub Setup

### 1. Add GitHub Secrets

Go to: Settings → Secrets → Actions

Add:
- `OPENAI_API_KEY` - Your OpenAI API key

### 2. Push Code

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git
git push -u origin main
```

## Building FAISS Indexes

For semantic search:

```bash
python scripts/create_faiss_index.py
```

Or in Docker:
```bash
docker-compose exec backend python /app/scripts/create_faiss_index.py
```

## Verification

1. Check health: `curl http://localhost:8000/health/ready`
2. Test API: `curl http://localhost:8000/docs`
3. Access frontend: http://localhost:8501

## Troubleshooting

See [Troubleshooting Guide](TROUBLESHOOTING.md)

