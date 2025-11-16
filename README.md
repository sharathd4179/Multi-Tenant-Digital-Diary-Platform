# Multi‑Tenant Digital Diary Platform with RAG‑Powered Knowledge Assistant

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-ready, multi-tenant digital diary application with RAG-powered semantic search, task extraction, and AI-powered insights.

## 🎯 Overview

This repository implements a full‑stack digital diary application designed for multi‑tenant deployments. A single backend serves multiple organisations (tenants) while logically isolating each tenant's data and configuration. Users can create, edit, search and summarise diary entries. A retrieval‑augmented generation (RAG) pipeline uses FAISS with a Hierarchical Navigable Small World (HNSW) index to provide fast semantic search with tenant‑aware filtering. Large language models (LLMs) are used to generate summaries, extract tasks and provide personalised insights.

**Multi‑tenancy** means that different organisations share the same application instance while keeping their data and configuration separate. To prevent cross‑tenant data leakage, the backend enforces tenant‑aware row‑level security and role‑based access control (RBAC). Only authorised users can access their tenant's resources.

## ✨ Features

### Multi‑Tenant Diary System

* **Tenants & Users:** The platform supports multiple tenants. Each user belongs to exactly one tenant. Two roles exist per tenant: `admin` and `user`. Tenant administrators can manage users within their tenant, while normal users can only manage their own notes.
* **Strict Isolation:** All database queries and vector index operations are scoped by `tenant_id`, ensuring that one tenant cannot see another tenant's data.
* **Role‑Based Access Control (RBAC):** Decorators ensure that only authorised users can perform particular actions. For example, only tenant admins can create or delete other users.

### Diary / Notes Functionality

* **CRUD Operations:** Create, read, update and delete diary entries. Notes support titles, markdown content, tags, timestamps and optional attachments.
* **Filtering & Pagination:** List notes with filters on date ranges, tags and keywords. Pagination is implemented for large note collections.
* **Analytics Dashboard:** View statistics, note frequency charts, task completion progress, and top tags.

### RAG‑Powered Knowledge Assistant

* **Semantic Search:** Notes are chunked into vector embeddings. A FAISS HNSW index stores these vectors for fast similarity search. Searches are filtered by tenant and optionally by user, date range or tags.
* **Summarisation & Task Extraction:** LangChain integrates OpenAI GPT‑4 to summarise notes and extract actionable tasks with optional due dates.
* **Context Optimisation:** The RAG pipeline includes logic to reduce context length by de‑duplicating similar chunks, reducing token usage.

### Infrastructure & Deployment

* **FastAPI Backend:** RESTful APIs with JWT authentication, SQLAlchemy, PostgreSQL, Redis
* **Streamlit Frontend:** User interface for creating notes, searching, viewing tasks and dashboards
* **Docker & Compose:** Containerized deployment with production-ready configurations
* **CI/CD Pipeline:** Automated testing and deployment with GitHub Actions
* **Health Monitoring:** Health check endpoints for production monitoring

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
   cd infrastructure/docker
   docker-compose up --build
   ```

4. **Access the app:**
   - **Frontend:** http://localhost:8501
   - **API Docs:** http://localhost:8000/docs
   - **Health Check:** http://localhost:8000/health/

📚 **For detailed setup, see [Complete Setup Guide](docs/SETUP.md)**

## 🛠️ Development

### Installation

```bash
# Install development dependencies
make install-dev

# Or using pip
pip install -e ".[dev]"
```

### Development Commands

```bash
# Run tests
make test

# Format code
make format

# Lint code
make lint

# Run database migrations
make migrate

# Seed demo data
make seed

# Build FAISS indexes
make index
```

See [Makefile](Makefile) for all available commands.

### Project Structure

```
multi-tenant-diary-assistant/
├── backend/              # Backend application (FastAPI)
│   ├── app/             # Application code
│   └── alembic/         # Database migrations
├── frontend/             # Frontend application (Streamlit)
├── tests/                # Test suite
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── infrastructure/       # Infrastructure configs
└── pipelines/            # Data pipelines
```

See [Project Structure](PROJECT_STRUCTURE.md) for detailed organization.

## 📚 Documentation

All documentation is organized in the [`docs/`](docs/) directory:

### Quick Links
- **[Quick Start](docs/QUICK_START.md)** - Get running in 5 minutes
- **[Setup Guide](docs/SETUP.md)** - Complete setup instructions
- **[User Guide](USAGE_GUIDE.md)** - How to use the application
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment

### Developer Resources
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Project Structure](PROJECT_STRUCTURE.md)** - Repository organization
- **[Changelog](CHANGELOG.md)** - Version history

### Security & Configuration
- **[Security Guide](docs/SECURITY.md)** - Security best practices
- **[API Key Setup](docs/API_KEY_SETUP.md)** - Configure API keys
- **[CI/CD Guide](docs/CI_CD.md)** - GitHub Actions setup

See [Documentation Index](docs/README.md) for complete list.

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
pytest tests/ -v --cov=backend.app --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py -v
```

## 🚢 Deployment

### GitHub Actions (Automatic)

1. Push code to `main` branch → Staging deployment
2. Tag version `v1.0.0` → Production deployment

See [CI/CD Guide](docs/CI_CD.md) for details.

### Manual Deployment

```bash
cd infrastructure/docker
docker-compose -f docker-compose.prod.yml up -d
```

See [Deployment Guide](DEPLOYMENT.md) for complete instructions.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add: amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Redis
- **Frontend:** Streamlit, Pandas, Matplotlib
- **AI/ML:** OpenAI API, LangChain, FAISS
- **Infrastructure:** Docker, Docker Compose, GitHub Actions
- **Testing:** Pytest, Coverage
- **Code Quality:** Black, Flake8, MyPy, Pre-commit

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Streamlit for the frontend framework
- OpenAI for the LLM capabilities
- FAISS for vector search

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/issues)
- **Documentation:** [docs/](docs/)
- **Discussions:** [GitHub Discussions](https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform/discussions)

---

**Made with ❤️ for multi-tenant diary management**
