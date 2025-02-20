import pytest
from datetime import date
from app.models.tenancy import Tenancy

class TestUpdateTenancy:
    """Tests for PUT /api/tenancies/<tenancy_id> endpoint."""

    def test_update_tenancy_success(self, client, session, landlord_token, test_tenancy_1):
        """Test successful update of tenancy details."""
        # Update data
        payload = {
            "rent_due": 1200.00,
            "lease_start_date": "2024-02-01",
            "lease_end_date": "2025-01-31"
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 200
        assert float(response.json["rent_due"]) == 1200.00
        assert response.json["lease_start_date"] == "2024-02-01"
        assert response.json["lease_end_date"] == "2025-01-31"

        # Verify database updates
        updated_tenancy = session.get(Tenancy, test_tenancy_1.tenancy_id)
        assert float(updated_tenancy.rent_due) == 1200.00
        assert updated_tenancy.lease_start_date == date(2024, 2, 1)
        assert updated_tenancy.lease_end_date == date(2025, 1, 31)

    def test_update_tenancy_partial(self, client, session, landlord_token, test_tenancy_1):
        """Test partial update of tenancy details."""
        # Update only rent_due
        payload = {
            "rent_due": 1200.00
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 200
        assert float(response.json["rent_due"]) == 1200.00
        assert response.json["lease_start_date"] == "2024-01-01"  # Unchanged
        assert response.json["lease_end_date"] == "2024-12-31"    # Unchanged

    def test_update_tenancy_remove_end_date(self, client, session, landlord_token, test_tenancy_1):
        """Test updating tenancy to remove end date."""
        # Set lease_end_date to null
        payload = {
            "lease_end_date": None
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 200
        assert response.json["lease_end_date"] is None

        # Verify database update
        updated_tenancy = session.get(Tenancy, test_tenancy_1.tenancy_id)
        assert updated_tenancy.lease_end_date is None

    def test_update_tenancy_invalid_dates(self, client, session, landlord_token, test_tenancy_1):
        """Test updating tenancy with invalid date format."""
        # Invalid date format
        payload = {
            "lease_start_date": "01-01-2024"  # Wrong format
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 400
        assert "Invalid lease_start_date format" in response.json["error"]

    def test_update_tenancy_end_before_start(self, client, session, landlord_token, test_tenancy_1):
        """Test updating tenancy with end date before start date."""
        # End date before start date
        payload = {
            "lease_start_date": "2024-02-01",
            "lease_end_date": "2024-01-01"
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Lease end date cannot be before start date"

    def test_update_tenancy_not_found(self, client, landlord_token):
        """Test updating non-existent tenancy."""
        payload = {
            "rent_due": 1200.00
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.put(
            "/api/tenancies/999",  # Non-existent ID
            json=payload,
            headers=headers
        )

        assert response.status_code == 404
        assert response.json["error"] == "Tenancy not found"

    def test_update_tenancy_unauthorized_role(self, client, auth_token, test_tenancy_1):
        """Test updating tenancy with unauthorized role (tenant)."""
        payload = {
            "rent_due": 1200.00
        }
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 403
        assert response.json["error"] == "Unauthorized"

    def test_update_tenancy_unauthorized_landlord(self, client, test_landlord_2, test_tenancy_1):
        """Test updating tenancy by a different landlord."""
        # Create token for different landlord
        with client.application.app_context():
            from flask_jwt_extended import create_access_token
            different_landlord_token = create_access_token(identity=str(test_landlord_2.user_id))

        payload = {
            "rent_due": 1200.00
        }
        headers = {"Authorization": f"Bearer {different_landlord_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 403
        assert response.json["error"] == "Unauthorized access to tenancy"

    def test_update_tenancy_no_token(self, client, test_tenancy_1):
        """Test updating tenancy without authentication token."""
        payload = {
            "rent_due": 1200.00
        }

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload
        )

        assert response.status_code == 401
        assert response.json["msg"] == "Missing Authorization Header"

    def test_update_tenancy_invalid_rent(self, client, landlord_token, test_tenancy_1):
        """Test updating tenancy with invalid rent value."""
        payload = {
            "rent_due": "invalid"
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Invalid rent_due value"

    def test_update_tenancy_empty_payload(self, client, landlord_token, test_tenancy_1):
        """Test updating tenancy with empty payload."""
        payload = {}
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "No update data provided"