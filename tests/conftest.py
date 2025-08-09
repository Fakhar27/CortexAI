"""
Pytest configuration and shared fixtures
This file is automatically loaded by pytest
"""

import pytest
import os
import tempfile
import shutil
from typing import Generator
from cortex import Client


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create a temporary database file for testing"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    yield db_path
    
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def client(temp_db_path) -> Client:
    """Create a test client with temporary database"""
    return Client(db_path=temp_db_path)


@pytest.fixture
def client_memory() -> Client:
    """Create a test client with in-memory storage"""
    return Client(db_path=None)


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing"""
    def _mock_env(**kwargs):
        for key, value in kwargs.items():
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, value)
    return _mock_env


@pytest.fixture
def sample_response():
    """Sample successful response for testing"""
    return {
        "id": "resp_test123",
        "status": "completed",
        "output": [{
            "id": "msg_test456",
            "content": [{
                "text": "Test response"
            }]
        }]
    }


# Markers for test organization
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: marks tests that need real API keys"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "critical: marks tests that are critical for release"
    )