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

# Import config AFTER setting TESTING env var
from app.config.config import DATABASE_URL
from pathlib import Path

sync_url = DATABASE_URL.replace("+aiosqlite", "")

# Performance optimization for SQLite in tests
sync_engine = create_engine(
    sync_url, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30,  
    } if "sqlite" in sync_url else {},
    pool_pre_ping=True,  
    pool_recycle=3600,
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
    
    # Cleanup: close all connections and reset
    try:
        await database.reset_db()
        # Explicitly close the async engine
        if hasattr(database, 'async_engine') and database.async_engine:
            await database.async_engine.dispose()
        # Close sync engine
        sync_engine.dispose()
    except Exception as e:
        print(f"[WARN] Cleanup warning: {e}")

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
async def auth_tokens(client):
    
    await reset()
    await init_db()
    
    # Get admin token first
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

    # Initialize system_info using the API endpoint (this ensures async visibility)
    set_balance_response = client.post(
        BASE_URL + "/balance/set",
        params={"amount": 10000.0},
        headers={"Authorization": tokens["admin"]}
    )
    
    if set_balance_response.status_code == 201:
        print("\n[OK] System info balance set to 10000.0 via API\n")
        
        # Verify it worked
        verify_response = client.get(
            BASE_URL + "/balance",
            headers={"Authorization": tokens["admin"]}
        )
        if verify_response.status_code == 200:
            balance = verify_response.json().get("balance", 0)
            print(f"[OK] System info verified - balance: {balance}\n")
    else:
        print(f"[WARN] Could not set system_info balance: {set_balance_response.status_code} - {set_balance_response.text}\n")

    return tokens
