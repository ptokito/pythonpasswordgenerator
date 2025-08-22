import pytest
from app import app, generate_password
import json

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the index route returns successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Password Generator' in response.data

def test_health_route(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b'OK'

def test_generate_route(client):
    """Test the password generation endpoint."""
    response = client.get('/generate')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'password' in data
    assert isinstance(data['password'], str)
    assert len(data['password']) == 12

def test_generate_password_function():
    """Test the password generation function."""
    # Test default parameters
    password = generate_password()
    assert len(password) == 12
    
    # Count special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    special_count = sum(1 for char in password if char in special_chars)
    assert special_count >= 3
    
    # Test custom length
    password = generate_password(length=20, special_chars=5)
    assert len(password) == 20
    
    # Test edge cases
    password = generate_password(length=4, special_chars=10)
    assert len(password) == 4
    
def test_password_contains_required_characters():
    """Test that generated passwords contain required character types."""
    password = generate_password()
    
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    assert has_lowercase
    assert has_uppercase
    assert has_digit
    assert has_special

def test_password_randomness():
    """Test that passwords are random (different each time)."""
    passwords = [generate_password() for _ in range(10)]
    # All passwords should be unique (with high probability)
    assert len(set(passwords)) == 10
