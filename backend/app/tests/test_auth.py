"""
Tests for authentication endpoints

To run tests:
    pytest backend/app/tests/test_auth.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_signup_success():
    """Test successful user registration"""
    response = client.post(
        "/api/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_signup_duplicate_email():
    """Test registration with duplicate email returns 409"""
    # First registration
    client.post(
        "/api/auth/signup",
        json={
            "name": "User One",
            "email": "duplicate@example.com",
            "password": "pass123"
        }
    )

    # Duplicate registration
    response = client.post(
        "/api/auth/signup",
        json={
            "name": "User Two",
            "email": "duplicate@example.com",
            "password": "pass456"
        }
    )
    assert response.status_code == 409


def test_login_success():
    """Test successful login returns token"""
    # Register user first
    client.post(
        "/api/auth/signup",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "loginpass"
        }
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "loginpass"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in_minutes" in data


def test_login_invalid_credentials():
    """Test login with wrong password returns 401"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user info with valid token"""
    # Register and login
    client.post(
        "/api/auth/signup",
        json={
            "name": "Current User",
            "email": "current@example.com",
            "password": "currentpass"
        }
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "current@example.com",
            "password": "currentpass"
        }
    )
    token = login_response.json()["access_token"]

    # Get user info
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"


def test_get_current_user_no_token():
    """Test accessing protected endpoint without token returns 401"""
    response = client.get("/api/auth/me")
    assert response.status_code in [401, 403]  # Depending on security implementation