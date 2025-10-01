import pytest
from app.models import User

def test_user_registration(client):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password': 'password123'
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'User registered successfully'
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['email'] == 'newuser@example.com'

def test_duplicate_email_registration(client):
    """Test registration with duplicate email"""
    user_data = {
        'email': 'duplicate@example.com',
        'username': 'user1',
        'password': 'password123'
    }

    # First registration
    response = client.post('/api/auth/register', json=user_data)
    assert response.status_code == 201

    # Duplicate email
    user_data['username'] = 'user2'
    response = client.post('/api/auth/register', json=user_data)
    assert response.status_code == 400
    assert 'Email already registered' in response.get_json()['error']

def test_user_login(client):
    """Test user login"""
    # Register user first
    client.post('/api/auth/register', json={
        'email': 'logintest@example.com',
        'username': 'loginuser',
        'password': 'password123'
    })

    # Test login
    response = client.post('/api/auth/login', json={
        'email': 'logintest@example.com',
        'password': 'password123'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Login successful'
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_invalid_login(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'wrongpass'
    })

    assert response.status_code == 401
    assert 'Invalid credentials' in response.get_json()['error']

def test_get_profile(client, auth_headers):
    """Test getting user profile"""
    response = client.get('/api/auth/profile', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['user']['email'] == 'test@example.com'

def test_update_profile(client, auth_headers):
    """Test updating user profile"""
    response = client.put('/api/auth/profile', headers=auth_headers, json={
        'preferred_currency': 'EUR',
        'email_notifications': False
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['user']['preferred_currency'] == 'EUR'
    assert data['user']['email_notifications'] == False

def test_change_password(client, auth_headers):
    """Test changing password"""
    response = client.post('/api/auth/change-password', headers=auth_headers, json={
        'current_password': 'testpass123',
        'new_password': 'newpass456'
    })

    assert response.status_code == 200
    assert 'Password changed successfully' in response.get_json()['message']

    # Test login with new password
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'newpass456'
    })
    assert response.status_code == 200

def test_token_refresh(client):
    """Test token refresh"""
    # Register and get tokens
    response = client.post('/api/auth/register', json={
        'email': 'refresh@example.com',
        'username': 'refreshuser',
        'password': 'password123'
    })
    refresh_token = response.get_json()['refresh_token']

    # Refresh token
    response = client.post('/api/auth/refresh', headers={
        'Authorization': f'Bearer {refresh_token}'
    })

    assert response.status_code == 200
    assert 'access_token' in response.get_json()