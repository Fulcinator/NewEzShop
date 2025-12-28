import os
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import database
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from main import app
from init_db import reset, init_db

# Set env before imports
os.environ["TESTING"] = "1"

# --- DATABASE URL CONFIGURATION ---
# Replace this with your actual DB connection string if not using SQLite
# For example: "postgresql://user:pass@localhost/dbname"
TEST_DATABASE_URL = "sqlite:///./test.db" 

sync_url = TEST_DATABASE_URL.replace("+asyncpg", "").replace("+aiosqlite", "")

sync_engine = create_engine(
    sync_url, 
    connect_args={"check_same_thread": False} if "sqlite" in sync_url else {}
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Initializes the schema for both Async and Sync engines."""
    from app.database.database import Base
    
    # 1. Initialize via Async
    await database.init_db()
    
    # 2. Initialize via Sync (This creates the missing tables for SaleRepository)
    # Base.metadata.create_all uses the sync_engine we defined earlier
    Base.metadata.create_all(bind=sync_engine)
    
    yield
    
    await database.reset_db()

@pytest.fixture
async def db_session():
    """Provides a clean async session for every test."""
    async with database.AsyncSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
def db_session_sync():
    """Provides a clean synchronous session for SaleRepository."""
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

BASE_URL = "http://127.0.0.1:8000/api/v1"

@pytest.fixture(scope="session")
def auth_tokens(client):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(reset())
    loop.run_until_complete(init_db())

    users = {
        "admin": {"username": "admin", "password": "admin"},
        "manager": {"username": "ShopManager", "password": "ShManager"},
        "cashier": {"username": "Cashier", "password": "Cashier"},
    }

    tokens = {}
    for role, creds in users.items():
        response = client.post(BASE_URL + "/auth", json=creds)
        assert response.status_code == 200
        tokens[role] = f"Bearer {response.json()['token']}"

    return tokens
