import pytest
import json
from app import app, generate_password

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the index route returns the HTML template."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'html' in response.data.lower()  # Check that HTML is returned

def test_health_route(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    # Parse JSON response
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'password-generator'

def test_generate_route(client):
    """Test the password generation endpoint."""
    test_data = {
        'length': 12,
        'include_uppercase': True,
        'include_lowercase': True,
        'include_numbers': True,
        'include_symbols': True
    }
    
    response = client.post('/generate', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'password' in data
    assert 'length' in data
    assert 'criteria' in data
    assert len(data['password']) == 12

def test_generate_route_invalid_length(client):
    """Test password generation with invalid length."""
    test_data = {
        'length': 2,  # Too short
        'include_uppercase': True,
        'include_lowercase': True,
        'include_numbers': True,
        'include_symbols': True
    }
    
    response = client.post('/generate', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_generate_password_function():
    """Test the generate_password function directly."""
    # Test with default parameters
    password = generate_password()
    assert len(password) == 12
    assert isinstance(password, str)
    
    # Test with custom length
    password = generate_password(length=20)
    assert len(password) == 20
    
    # Test with specific criteria
    password = generate_password(
        length=16,
        include_uppercase=True,
        include_lowercase=True,
        include_numbers=True,
        include_symbols=True
    )
    assert len(password) == 16

def test_password_contains_required_characters():
    """Test that generated passwords contain required character types."""
    password = generate_password(
        length=16,
        include_uppercase=True,
        include_lowercase=True,
        include_numbers=True,
        include_symbols=True
    )
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    assert has_upper, "Password should contain uppercase letters"
    assert has_lower, "Password should contain lowercase letters"
    assert has_digit, "Password should contain digits"
    assert has_symbol, "Password should contain symbols"

def test_password_randomness():
    """Test that generated passwords are different (randomness check)."""
    passwords = [generate_password(length=12) for _ in range(10)]
    
    # All passwords should be different
    assert len(set(passwords)) == len(passwords), "Passwords should be random and unique"

def test_generate_minimal_criteria():
    """Test password generation with minimal criteria."""
    # Test with only lowercase
    password = generate_password(
        length=8,
        include_uppercase=False,
        include_lowercase=True,
        include_numbers=False,
        include_symbols=False
    )
    assert len(password) == 8
    assert all(c.islower() or c.isalpha() for c in password)

def test_generate_no_criteria():
    """Test password generation when no criteria are specified."""
    password = generate_password(
        length=12,
        include_uppercase=False,
        include_lowercase=False,
        include_numbers=False,
        include_symbols=False
    )
    # Should default to all character types
    assert len(password) == 12
    assert isinstance(password, str)
