"""Setup configuration for multi-tenant-diary-assistant."""
from setuptools import find_packages, setup

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="multi-tenant-diary-assistant",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Multi-tenant digital diary platform with RAG-powered knowledge assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sharathd4179/Multi-Tenant-Digital-Diary-Platform",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.29.0",
        "sqlalchemy>=2.0.29",
        "psycopg2-binary>=2.9.9",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "pydantic>=2.6.4",
        "pydantic-settings>=2.1.0",
        "email-validator>=2.1.0",
        "langchain>=0.1.14",
        "openai>=1.24.0",
        "faiss-cpu>=1.7.4",
        "redis>=5.0.1",
        "slowapi>=0.1.9",
        "alembic>=1.13.1",
        "python-multipart>=0.0.9",
    ],
    extras_require={
        "dev": [
            "pytest>=8.1.1",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.23.3",
            "httpx>=0.27.0",
            "black>=24.3.0",
            "flake8>=7.0.0",
            "mypy>=1.9.0",
            "isort>=5.13.2",
        ],
        "frontend": [
            "streamlit>=1.33.0",
            "pandas>=2.2.1",
            "matplotlib>=3.8.3",
        ],
    },
)

