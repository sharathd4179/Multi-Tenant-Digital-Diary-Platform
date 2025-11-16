# Multi‑Tenant Digital Diary Platform with RAG‑Powered Knowledge Assistant

## Overview

This repository implements a full‑stack digital diary application designed for multi‑tenant deployments.  A single backend serves multiple organisations (tenants) while logically isolating each tenant’s data and configuration.  Users can create, edit, search and summarise diary entries.  A retrieval‑augmented generation (RAG) pipeline uses FAISS with a Hierarchical Navigable Small World (HNSW) index to provide fast semantic search with tenant‑aware filtering【897976156503739†L26-L32】.  Large language models (LLMs) are used to generate summaries, extract tasks and provide personalised insights.

Multi‑tenancy means that different organisations share the same application instance while keeping their data and configuration separate【471798880420436†L76-L103】.  To prevent cross‑tenant data leakage, the backend enforces tenant‑aware row‑level security and role‑based access control (RBAC)【471798880420436†L133-L156】.  Only authorised users can access their tenant’s resources.

## Features

### Multi‑Tenant Diary System

* **Tenants & Users:** The platform supports multiple tenants.  Each user belongs to exactly one tenant.  Two roles exist per tenant: `admin` and `user`.  Tenant administrators can manage users within their tenant, while normal users can only manage their own notes.
* **Strict Isolation:** All database queries and vector index operations are scoped by `tenant_id`, ensuring that one tenant cannot see another tenant’s data【471798880420436†L133-L156】.
* **Role‑Based Access Control (RBAC):** Decorators ensure that only authorised users can perform particular actions.  For example, only tenant admins can create or delete other users.

### Diary / Notes Functionality

* **CRUD Operations:** Create, read, update and delete diary entries.  Notes support titles, markdown content, tags, timestamps and optional attachments (file metadata stub).
* **Filtering & Pagination:** List notes with filters on date ranges, tags and keywords.  Pagination is implemented for large note collections.
* **Basic Analytics:** Endpoints return simple statistics (e.g. number of notes, last activity) per tenant.

### RAG‑Powered Knowledge Assistant

* **Semantic Search:** Notes are chunked into vector embeddings.  A FAISS HNSW index (using `M=32` and `ef_construction=200` by default) stores these vectors.  HNSW provides top‑performing search speeds and recall for vector similarity search【897976156503739†L26-L32】.  Searches are filtered by tenant and optionally by user, date range or tags.
* **Summarisation & Task Extraction:** LangChain integrates OpenAI GPT‑4 (or any compatible model) to summarise individual notes, aggregates (day/week/month) and search results.  A specialised prompt extracts actionable tasks with optional due dates.  Extracted tasks are stored and can be marked as complete.
* **Context Optimisation:** The RAG pipeline includes logic to reduce context length by de‑duplicating similar chunks, removing boilerplate and using metadata filters before vector search.  This reduces token usage during LLM calls.

### Personalised Insights & Dashboard

* **Analytics:** A simple analytics module computes sentiment (via a heuristic scoring function), note frequency over time and top tags.  Results are displayed in the Streamlit dashboard.
* **Tasks:** Users can view open and completed tasks extracted from their notes.
* **Semantic Assistant:** A chat‑like interface allows users to ask natural language questions.  The assistant retrieves relevant notes via the RAG pipeline and generates answers using GPT‑4.

### Pipelines & Data Engineering

* **BigQuery Schemas:** Example schema definitions for storing notes, embeddings and LLM call logs in BigQuery.  These tables support offline analytics at scale.
* **Spark Job:** A PySpark script reads new or updated notes from BigQuery, generates embeddings in batches and writes back metadata.  It can be scheduled via cron or a cloud scheduler.

### Infrastructure & Deployment

* **FastAPI Backend:** Provides RESTful APIs with JWT authentication.  SQLAlchemy models interact with PostgreSQL.  Redis caches retrieval results.  Tests are written with `pytest`.
* **Streamlit Front‑End:** Implements the user interface for creating notes, searching, viewing tasks and dashboards.  The front‑end authenticates against the backend and uses the APIs.
* **Docker & Compose:** `docker-compose.yml` orchestrates PostgreSQL, Redis, the backend and the Streamlit front‑end.  Environment variables are configured via `.env` files.
* **Sample Data & Scripts:** Scripts are provided to seed the database with demo data, build FAISS indexes and benchmark retrieval latency.

## 🚀 Quick Start

Get started in 5 minutes! See [Quick Start Guide](docs/QUICK_START.md) for detailed instructions.

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (optional, for RAG features)
- Git (for deployment)

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform.git
   cd Multi-Tenant-Digital-Diary-Platform
   ```

2. **Create `.env` file:**
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/diarydb
   REDIS_URL=redis://localhost:6379/0
   JWT_SECRET_KEY=your_minimum_32_character_secret_key
   OPENAI_API_KEY=sk-your-openai-api-key
   ENVIRONMENT=development
   ```

3. **Start services:**
   ```bash
   cd infra
   docker-compose up --build
   ```

4. **Access the app:**
   - **Frontend:** http://localhost:8501
   - **API Docs:** http://localhost:8000/docs
   - **Health Check:** http://localhost:8000/health/

📚 **For detailed setup, see [Complete Setup Guide](docs/SETUP.md)**

### Local Development

To run the backend and front‑end without Docker:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run database migrations (using Alembic or SQLAlchemy metadata)
uvicorn backend.app.main:app --reload

# In another terminal for Streamlit
streamlit run frontend/streamlit_app.py
```

### Running Tests

Tests are located in `backend/app/tests/`.  Use pytest to run them:

```bash
pytest -q
```

## 📚 Documentation

All documentation is organized in the [`docs/`](docs/) directory:

- **[Quick Start](docs/QUICK_START.md)** - Get running in 5 minutes
- **[Setup Guide](docs/SETUP.md)** - Complete setup instructions
- **[Security Guide](docs/SECURITY.md)** - Security best practices
- **[API Key Setup](docs/API_KEY_SETUP.md)** - Configure API keys
- **[CI/CD Guide](docs/CI_CD.md)** - GitHub Actions setup
- **[Usage Guide](USAGE_GUIDE.md)** - How to use the application
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment

See [Documentation Index](docs/README.md) for complete list.

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository and create a new branch
2. Make your changes with clear commits
3. Ensure tests pass: `pytest backend/app/tests/`
4. Update documentation as needed
5. Open a pull request describing your changes

## License

This project is licensed under the MIT License.  See the [LICENSE](LICENSE) file for details.
