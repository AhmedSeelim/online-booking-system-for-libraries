"""
Tests for book purchase endpoints

To run tests:
    pytest backend/app/tests/test_purchase.py -v
"""

import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)


@pytest.fixture
def user_token():
    """Fixture to get user authentication token"""
    # Register user
    client.post(
        "/api/auth/signup",
        json={
            "name": "Purchase User",
            "email": "purchaseuser@example.com",
            "password": "purchasepass"
        }
    )

    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={
            "email": "purchaseuser@example.com",
            "password": "purchasepass"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token():
    """Fixture to get admin authentication token"""
    # Register admin user
    client.post(
        "/api/auth/signup",
        json={
            "name": "Purchase Admin",
            "email": "purchaseadmin@example.com",
            "password": "adminpass"
        }
    )

    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={
            "email": "purchaseadmin@example.com",
            "password": "adminpass"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def test_book_with_stock(admin_token):
    """Fixture to create a test book with stock"""
    response = client.post(
        "/api/books",
        json={
            "title": "Test Book for Purchase",
            "author": "Test Author",
            "isbn": "978-1234567899",
            "category": "Technology",
            "description": "A test book with stock",
            "stock_count": 10
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return response.json()


@pytest.fixture
def test_book_low_stock(admin_token):
    """Fixture to create a test book with low stock"""
    response = client.post(
        "/api/books",
        json={
            "title": "Low Stock Book",
            "author": "Test Author",
            "isbn": "978-9876543211",
            "category": "Fiction",
            "description": "A book with limited stock",
            "stock_count": 2
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return response.json()


def test_purchase_success(user_token, test_book_with_stock):
    """Test successful book purchase"""
    book_id = test_book_with_stock["id"]
    initial_stock = test_book_with_stock["stock_count"]

    # Purchase 1 copy
    response = client.post(
        f"/api/books/{book_id}/purchase",
        json={"quantity": 1},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "transaction_id" in data
    assert data["book_id"] == book_id
    assert data["book_title"] == test_book_with_stock["title"]
    assert data["quantity"] == 1
    assert data["amount"] > 0
    assert data["currency"] == "USD"
    assert data["status"] == "completed"

    # Verify stock was decremented
    book_response = client.get(f"/api/books/{book_id}")
    updated_book = book_response.json()
    assert updated_book["stock_count"] == initial_stock - 1


def test_purchase_multiple_copies(user_token, test_book_with_stock):
    """Test purchasing multiple copies in one transaction"""
    book_id = test_book_with_stock["id"]
    quantity = 3

    # Get initial stock
    book_response = client.get(f"/api/books/{book_id}")
    initial_stock = book_response.json()["stock_count"]

    # Purchase multiple copies
    response = client.post(
        f"/api/books/{book_id}/purchase",
        json={"quantity": quantity},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == quantity

    # Verify stock was decremented correctly
    book_response = client.get(f"/api/books/{book_id}")
    updated_book = book_response.json()
    assert updated_book["stock_count"] == initial_stock - quantity


def test_purchase_out_of_stock(user_token, test_book_low_stock):
    """Test that purchasing more than available stock returns 400"""
    book_id = test_book_low_stock["id"]
    available_stock = test_book_low_stock["stock_count"]

    # Attempt to purchase more than available
    response = client.post(
        f"/api/books/{book_id}/purchase",
        json={"quantity": available_stock + 5},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 400
    assert "insufficient stock" in response.json()["detail"].lower()

    # Verify stock was NOT decremented
    book_response = client.get(f"/api/books/{book_id}")
    current_book = book_response.json()
    assert current_book["stock_count"] == available_stock


def test_purchase_exact_stock(user_token, test_book_low_stock):
    """Test purchasing exact available stock"""
    book_id = test_book_low_stock["id"]
    available_stock = test_book_low_stock["stock_count"]

    # Purchase all available stock
    response = client.post(
        f"/api/books/{book_id}/purchase",
        json={"quantity": available_stock},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200

    # Verify stock is now 0
    book_response = client.get(f"/api/books/{book_id}")
    updated_book = book_response.json()
    assert updated_book["stock_count"] == 0


def test_purchase_when_out_of_stock(user_token, admin_token):
    """Test purchasing from a book with 0 stock"""
    # Create book with 0 stock
    create_response = client.post(
        "/api/books",
        json={
            "title": "Out of Stock Book",
            "author": "Test Author",
            "isbn": "978-0000000000",
            "category": "Fiction",
            "stock_count": 0
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    book_id = create_response.json()["id"]

    # Attempt to purchase
    response = client.post(
        f"/api/books/{book_id}/purchase",
        json={"quantity": 1},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 400
    assert "insufficient stock" in response.json()["detail"].lower()


def test_purchase_invalid_quantity_zero(user_token, test_book_with_stock):
    """Test that quantity must be at least 1"""
    book_id = test_book_with_stock["id"]

    response = client.post(
        f"/api/books/{book_id}/purchase",
        json={"quantity": 0},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    # Should fail validation (422 Unprocessable Entity)
    assert response.status_code == 422


def test_purchase_invalid_quantity_negative(user_token, test_book_with_stock):
    """Test that quantity cannot be negative"""
    book_id = test_book_with_stock["id"]

    response = client.post(
        f"/api/books/{book_id}/purchase",
        json={"quantity": -5},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    # Should fail validation (422 Unprocessable Entity)
    assert response.status_code == 422


def test_purchase_nonexistent_book(user_token):
    """Test purchasing a book that doesn't exist"""
    response = client.post(
        "/api/books/99999/purchase",
        json={"quantity": 1},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_purchase_without_authentication(test_book_with_stock):
    """Test that purchase requires authentication"""
    book_id = test_book_with_stock["id"]

    response = client.post(
        f"/api/books/{book_id}/purchase",
        json={"quantity": 1}
    )

    # Should return 401 or 403
    assert response.status_code in [401, 403]


def test_purchase_transaction_atomicity(user_token, admin_token):
    """Test that purchase is atomic (stock and transaction together)"""
    # Create book with exactly 1 stock
    create_response = client.post(
        "/api/books",
        json={
            "title": "Atomic Test Book",
            "author": "Test Author",
            "isbn": "978-1111111112",
            "category": "Technology",
            "stock_count": 1
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    book_id = create_response.json()["id"]

    # Purchase the only copy
    response = client.post(
        f"/api/books/{book_id}/purchase",
        json={"quantity": 1},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200
    transaction_id = response.json()["transaction_id"]
    assert transaction_id is not None

    # Verify stock is 0
    book_response = client.get(f"/api/books/{book_id}")
    assert book_response.json()["stock_count"] == 0

    # Verify another purchase fails
    second_purchase = client.post(
        f"/api/books/{book_id}/purchase",
        json={"quantity": 1},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert second_purchase.status_code == 400