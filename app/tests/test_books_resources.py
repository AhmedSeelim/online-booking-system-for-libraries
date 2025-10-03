"""
Tests for books and resources endpoints

To run tests:
    pytest backend/app/tests/test_books_resources.py -v
"""

import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)


@pytest.fixture
def admin_token():
    """Fixture to get admin authentication token"""
    # Register admin user
    client.post(
        "/api/auth/signup",
        json={
            "name": "Admin",
            "email": "admin_test@example.com",
            "password": "adminpass"
        }
    )

    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={
            "email": "admin_test@example.com",
            "password": "adminpass"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def regular_user_token():
    """Fixture to get regular user authentication token"""
    # Register regular user
    client.post(
        "/api/auth/signup",
        json={
            "name": "Regular User",
            "email": "user_test@example.com",
            "password": "userpass"
        }
    )

    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={
            "email": "user_test@example.com",
            "password": "userpass"
        }
    )
    return response.json()["access_token"]


# Books Tests

def test_list_books():
    """Test listing books (public endpoint)"""
    response = client.get("/api/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_books_with_search():
    """Test searching books by query"""
    response = client.get("/api/books?q=python&category=Technology")
    assert response.status_code == 200


def test_list_books_pagination():
    """Test books pagination"""
    response = client.get("/api/books?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10


def test_create_book_as_admin(admin_token):
    """Test creating book as admin user"""
    response = client.post(
        "/api/books",
        json={
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "978-1234567890",
            "category": "Technology",
            "description": "A test book",
            "stock_count": 5
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"


def test_create_book_as_regular_user_forbidden(regular_user_token):
    """Test that regular users cannot create books (403)"""
    response = client.post(
        "/api/books",
        json={
            "title": "Unauthorized Book",
            "author": "Test Author",
            "isbn": "978-9876543210",
            "category": "Fiction",
            "stock_count": 1
        },
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == 403


def test_get_book_by_id():
    """Test getting a specific book"""
    # Assumes book with ID 1 exists (from seed data or previous tests)
    response = client.get("/api/books/1")
    # Could be 200 (found) or 404 (not found) depending on test order
    assert response.status_code in [200, 404]


def test_update_book_as_admin(admin_token):
    """Test updating book as admin"""
    # Create book first
    create_response = client.post(
        "/api/books",
        json={
            "title": "Original Title",
            "author": "Author",
            "isbn": "978-1111111111",
            "category": "Fiction",
            "stock_count": 3
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    book_id = create_response.json()["id"]

    # Update book
    response = client.put(
        f"/api/books/{book_id}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_delete_book_as_admin(admin_token):
    """Test deleting book as admin"""
    # Create book first
    create_response = client.post(
        "/api/books",
        json={
            "title": "To Delete",
            "author": "Author",
            "isbn": "978-2222222222",
            "category": "Fiction",
            "stock_count": 1
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    book_id = create_response.json()["id"]

    # Delete book
    response = client.delete(
        f"/api/books/{book_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204


# Resources Tests

def test_list_resources():
    """Test listing resources"""
    response = client.get("/api/resources")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_resources_with_capacity_filter():
    """Test filtering resources by minimum capacity"""
    response = client.get("/api/resources?min_capacity=5")
    assert response.status_code == 200


def test_create_resource_as_admin(admin_token):
    """Test creating resource as admin"""
    response = client.post(
        "/api/resources",
        json={
            "name": "Test Room",
            "type": "room",
            "capacity": 10,
            "features": '{"projector": true}',
            "open_hour": "09:00",
            "close_hour": "18:00"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201


def test_create_resource_as_regular_user_forbidden(regular_user_token):
    """Test that regular users cannot create resources (403)"""
    response = client.post(
        "/api/resources",
        json={
            "name": "Unauthorized Resource",
            "type": "seat",
            "capacity": 1
        },
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == 403


def test_get_resource_by_id():
    """Test getting a specific resource"""
    response = client.get("/api/resources/1")
    assert response.status_code in [200, 404]


def test_update_resource_as_admin(admin_token):
    """Test updating resource as admin"""
    # Create resource first
    create_response = client.post(
        "/api/resources",
        json={
            "name": "Original Resource",
            "type": "equipment",
            "capacity": 1
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    resource_id = create_response.json()["id"]

    # Update resource
    response = client.put(
        f"/api/resources/{resource_id}",
        json={"name": "Updated Resource"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


def test_delete_resource_as_admin(admin_token):
    """Test deleting resource as admin"""
    # Create resource first
    create_response = client.post(
        "/api/resources",
        json={
            "name": "To Delete Resource",
            "type": "seat",
            "capacity": 1
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    resource_id = create_response.json()["id"]

    # Delete resource
    response = client.delete(
        f"/api/resources/{resource_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204