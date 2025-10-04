"""
Tests for booking endpoints

To run tests:
    pytest backend/app/tests/test_booking.py -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from ..main import app

client = TestClient(app)


@pytest.fixture
def user_token():
    """Fixture to get user authentication token"""
    # Register user
    client.post(
        "/api/auth/signup",
        json={
            "name": "Booking User",
            "email": "bookinguser@example.com",
            "password": "bookingpass"
        }
    )

    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={
            "email": "bookinguser@example.com",
            "password": "bookingpass"
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
            "name": "Booking Admin",
            "email": "bookingadmin@example.com",
            "password": "adminpass"
        }
    )

    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={
            "email": "bookingadmin@example.com",
            "password": "adminpass"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def test_resource(admin_token):
    """Fixture to create a test resource"""
    response = client.post(
        "/api/resources",
        json={
            "name": "Test Booking Room",
            "type": "room",
            "capacity": 5,
            "open_hour": "09:00",
            "close_hour": "18:00"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return response.json()


def test_booking_success(user_token, test_resource):
    """Test successful booking creation"""
    # Create booking for 2 hours from now
    start_time = datetime.now(timezone.utc) + timedelta(hours=2)
    end_time = start_time + timedelta(hours=1)

    response = client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
            "notes": "Test booking"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["resource_id"] == test_resource["id"]
    assert data["status"] == "confirmed"
    assert data["notes"] == "Test booking"


def test_booking_overlap_conflict(user_token, test_resource):
    """Test that overlapping bookings are rejected with 409"""
    # Create first booking
    start_time = datetime.now(timezone.utc) + timedelta(hours=3)
    end_time = start_time + timedelta(hours=2)

    first_response = client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert first_response.status_code == 201

    # Attempt overlapping booking (1 hour into first booking)
    overlap_start = start_time + timedelta(hours=1)
    overlap_end = overlap_start + timedelta(hours=1)

    overlap_response = client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": overlap_start.isoformat(),
            "end_datetime": overlap_end.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert overlap_response.status_code == 409
    assert "not available" in overlap_response.json()["detail"].lower()


def test_booking_contiguous_allowed(user_token, test_resource):
    """Test that contiguous bookings (end == start) are allowed"""
    # Create first booking
    start_time1 = datetime.now(timezone.utc) + timedelta(hours=4)
    end_time1 = start_time1 + timedelta(hours=1)

    first_response = client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": start_time1.isoformat(),
            "end_datetime": end_time1.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert first_response.status_code == 201

    # Create contiguous booking (starts exactly when first ends)
    start_time2 = end_time1
    end_time2 = start_time2 + timedelta(hours=1)

    second_response = client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": start_time2.isoformat(),
            "end_datetime": end_time2.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert second_response.status_code == 201


def test_booking_validation_start_before_end(user_token, test_resource):
    """Test validation: start must be before end"""
    start_time = datetime.now(timezone.utc) + timedelta(hours=2)
    end_time = start_time - timedelta(hours=1)  # End before start!

    response = client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 400
    assert "before end" in response.json()["detail"].lower()


def test_booking_validation_max_duration(user_token, test_resource):
    """Test validation: booking cannot exceed max duration (8 hours)"""
    start_time = datetime.now(timezone.utc) + timedelta(hours=2)
    end_time = start_time + timedelta(hours=9)  # 9 hours - exceeds limit

    response = client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 400
    assert "duration" in response.json()["detail"].lower()


def test_booking_validation_min_lead_time(user_token, test_resource):
    """Test validation: booking must be at least 15 minutes in advance"""
    start_time = datetime.now(timezone.utc) + timedelta(minutes=5)  # Only 5 minutes ahead
    end_time = start_time + timedelta(hours=1)

    response = client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 400
    assert "advance" in response.json()["detail"].lower()


def test_list_user_bookings(user_token, test_resource):
    """Test listing user's bookings"""
    # Create a booking
    start_time = datetime.now(timezone.utc) + timedelta(hours=5)
    end_time = start_time + timedelta(hours=1)

    client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    # List bookings
    response = client.get(
        "/api/bookings",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200
    bookings = response.json()
    assert isinstance(bookings, list)
    assert len(bookings) > 0


def test_cancel_booking_success(user_token, test_resource):
    """Test successful booking cancellation"""
    # Create booking far enough in future (2 hours)
    start_time = datetime.now(timezone.utc) + timedelta(hours=2)
    end_time = start_time + timedelta(hours=1)

    create_response = client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    booking_id = create_response.json()["id"]

    # Cancel booking
    cancel_response = client.delete(
        f"/api/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"


def test_cancel_booking_too_late(user_token, test_resource):
    """Test that cancellation fails if too close to start time"""
    # Create booking only 30 minutes in future (less than 1 hour cancellation window)
    start_time = datetime.now(timezone.utc) + timedelta(minutes=30)
    end_time = start_time + timedelta(hours=1)

    create_response = client.post(
        "/api/bookings",
        json={
            "resource_id": test_resource["id"],
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    booking_id = create_response.json()["id"]

    # Attempt to cancel (should fail due to cancellation window)
    cancel_response = client.delete(
        f"/api/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert cancel_response.status_code == 400
    assert "cancel" in cancel_response.json()["detail"].lower()


def test_check_availability_specific_time(test_resource):
    """Test checking availability for specific time range"""
    start_time = datetime.now(timezone.utc) + timedelta(hours=6)
    end_time = start_time + timedelta(hours=1)

    response = client.get(
        f"/api/resources/{test_resource['id']}/availability",
        params={
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert isinstance(data["available"], bool)


def test_check_availability_by_date(test_resource):
    """Test getting available slots for a specific date"""
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")

    response = client.get(
        f"/api/resources/{test_resource['id']}/availability",
        params={"date": tomorrow}
    )

    assert response.status_code == 200
    data = response.json()
    assert "slots" in data
    assert isinstance(data["slots"], list)
    if len(data["slots"]) > 0:
        assert "start" in data["slots"][0]
        assert "end" in data["slots"][0]
        assert "available" in data["slots"][0]