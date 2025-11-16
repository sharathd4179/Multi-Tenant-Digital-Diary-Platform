"""
Populate the database with sample tenants, users and notes.

This script is intended for local development and demos.  It connects to the
database specified by `DATABASE_URL`, creates a few tenants, users and notes,
and then exits.  If the tables do not exist, they will be created.
"""
import os
import random
from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.core.config import Settings
from backend.app.models import base as base_model
from backend.app.models.tenant import Tenant
from backend.app.models.user import User
from backend.app.models.note import Note


TENANT_NAMES = ["Acme Corp", "Globex", "Umbrella", "Initech"]
USERNAMES = ["alice", "bob", "carol", "dave", "eve"]
SAMPLE_CONTENT = [
    "Today I started working on the new project. Need to set up the database and API.",
    "Meeting with the team went well. Action items: update the documentation and fix the login bug.",
    "Feeling productive! Completed the dashboard design and pushed it to the repo.",
    "Need to research how FAISS HNSW works and integrate it into our search.",
    "Summary of the week: deployed the first version of the app, wrote tests, and fixed deployment scripts."
]


def seed():
    db_url = os.getenv("DATABASE_URL")
    engine = sa.create_engine(db_url)
    base_model.Base.metadata.create_all(bind=engine)
    session = Session(engine)

    # Create tenants
    tenants = []
    for name in TENANT_NAMES:
        tenant = Tenant(name=name)
        session.add(tenant)
        tenants.append(tenant)
    session.commit()

    # Create users for each tenant
    for tenant in tenants:
        for username in USERNAMES:
            email = f"{username}@{tenant.name.replace(' ', '').lower()}.com"
            user = User(
                tenant_id=tenant.id,
                username=username,
                email=email,
                hashed_password=get_password_hash("password"),
                role="admin" if username == "alice" else "user",
            )
            session.add(user)
        session.commit()

    # Create notes for each user
    users = session.query(User).all()
    for user in users:
        for _ in range(5):
            content = random.choice(SAMPLE_CONTENT)
            note = Note(
                tenant_id=user.tenant_id,
                user_id=user.id,
                title="Diary Entry",
                content=content,
                tags=["sample", "demo"],
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                updated_at=datetime.utcnow(),
            )
            session.add(note)
        session.commit()

    print("Demo data seeded successfully")


if __name__ == "__main__":
    seed()