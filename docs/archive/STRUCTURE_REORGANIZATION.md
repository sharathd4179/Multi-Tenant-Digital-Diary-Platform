# 🏗️ Repository Structure Reorganization Plan

## 🎯 Goal

Transform the repository into an industry-standard, production-ready structure following Python/FastAPI best practices.

## 📋 Current Issues

1. ❌ Too many markdown files in root (30+ files)
2. ❌ Scripts scattered across root
3. ❌ Documentation not well organized
4. ❌ Missing standard Python project files
5. ❌ No clear separation of concerns
6. ❌ Tests mixed with source code

## ✅ Target Structure

```
multi-tenant-diary-assistant/
├── .github/
│   └── workflows/          # CI/CD (already good)
│
├── src/                     # Source code
│   ├── backend/            # Backend application
│   │   ├── app/           # FastAPI app
│   │   └── alembic/       # Migrations
│   └── frontend/          # Frontend app
│
├── tests/                   # All tests
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/                    # All documentation
│   ├── guides/
│   ├── api/
│   ├── deployment/
│   └── development/
│
├── scripts/                  # Utility scripts
│   ├── setup/
│   ├── deployment/
│   └── maintenance/
│
├── infrastructure/          # Infrastructure configs
│   └── docker/             # Docker compose files
│
├── config/                  # Configuration files
│   └── environments/
│
├── pipelines/              # Data pipelines (keep as is)
│
├── pyproject.toml         # Python project config ✅
├── setup.py               # Package setup ✅
├── Makefile               # Development commands ✅
├── .pre-commit-config.yaml # Code quality hooks ✅
├── CHANGELOG.md           # Version history ✅
├── CONTRIBUTING.md        # Contribution guide ✅
├── requirements.txt       # Dependencies
├── requirements-dev.txt   # Dev dependencies
├── README.md              # Main README
└── LICENSE                # License
```

## 🔄 Migration Steps

### Phase 1: Create New Structure ✅
- [x] Create `pyproject.toml`
- [x] Create `setup.py`
- [x] Create `Makefile`
- [x] Create `.pre-commit-config.yaml`
- [x] Create `CHANGELOG.md`
- [x] Create `CONTRIBUTING.md`

### Phase 2: Reorganize Files (Next)
- [ ] Move all docs to `docs/` subdirectories
- [ ] Move scripts to `scripts/` subdirectories
- [ ] Move infrastructure to `infrastructure/`
- [ ] Move tests to `tests/`
- [ ] Create `config/` directory

### Phase 3: Update References
- [ ] Update all import paths
- [ ] Update Dockerfile paths
- [ ] Update CI/CD paths
- [ ] Update documentation links

### Phase 4: Clean Up
- [ ] Remove redundant files
- [ ] Update README
- [ ] Verify everything works

## 📝 File Organization

### Documentation → `docs/`
- `docs/guides/` - User guides
- `docs/api/` - API documentation
- `docs/deployment/` - Deployment guides
- `docs/development/` - Developer guides

### Scripts → `scripts/`
- `scripts/setup/` - Setup scripts
- `scripts/deployment/` - Deployment scripts
- `scripts/maintenance/` - Maintenance scripts

### Infrastructure → `infrastructure/`
- `infrastructure/docker/` - Docker compose files
- `infrastructure/kubernetes/` - K8s (optional)
- `infrastructure/terraform/` - Terraform (optional)

## ✅ Benefits

1. **Professional** - Industry-standard structure
2. **Scalable** - Easy to add new features
3. **Maintainable** - Clear organization
4. **Discoverable** - Easy to find files
5. **Standard** - Follows Python/FastAPI conventions

## 🚀 Next Steps

1. Review and approve structure
2. Execute migration
3. Test everything works
4. Update documentation
5. Commit and push

