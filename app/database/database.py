from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
from app.config.config import DATABASE_URL
import importlib
import pkgutil
import app.models.DAO as dao_package

# --- Create the async engine ---
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # set to True if you want SQL logs
    future=True,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
    } if "sqlite" in DATABASE_URL else {}
)

# For SQLite, set pragmas to improve concurrency
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA read_uncommitted=1")
        cursor.close()

# --- Create the async session maker ---
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession
)

# --- Declare the Base for ORM models ---
Base = declarative_base()

# --- Dependency function for FastAPI routes ---
async def get_db():
    """FastAPI dependency to get an async database session."""
    async with AsyncSessionLocal() as session:
        yield session

def _import_all_daos():
    """Importa dinamicamente tutti i moduli DAO."""
    package_path = dao_package.__path__
    package_name = dao_package.__name__
    for _, module_name, _ in pkgutil.iter_modules(package_path):
        importlib.import_module(f"{package_name}.{module_name}")

async def init_db():
    _import_all_daos()
    #from app.models.DAO import DAO  # ensure all models imported
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def reset_db():
    """Drop all tables and recreate them (resets database to empty state)."""
    from app.models import DAO  # ensure all models imported
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)