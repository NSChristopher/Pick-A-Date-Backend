import pytest
from backend.app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        # Establish an application context before running the tests.
        with app.app_context():
            # Create all tables for testing
            db.create_all()

        yield client
        
        # Drop all tables after the test
        with app.app_context():
            db.drop_all()