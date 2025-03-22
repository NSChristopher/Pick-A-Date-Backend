# tests/conftest.py
import pytest
from backend.app import create_app, db

@pytest.fixture
def client():
    app = create_app('testing')

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()
