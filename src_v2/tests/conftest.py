import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src_v2.main import app
from src_v2.user.infrastructure.db.config import Base, get_db

# 1. Configuración de la base de datos de prueba (en memoria es más rápida)
# Si prefieres archivo, usa: f"sqlite:///./test.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Crea una base de datos nueva para cada test."""
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Override de la dependencia get_db antes de cada test."""
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    # Aquí ocurre la magia de FastAPI
    app.dependency_overrides[get_db] = _get_test_db
    
    with TestClient(app) as c:
        yield c
    
    # Limpiamos los overrides después del test
    app.dependency_overrides.clear()