from datetime import date
from app.models.tenancy import Tenancy

class TestUpdateTenancy:
    """Tests for PUT /api/tenancies/<tenancy_id> endpoint."""

    def test_update_tenancy_success(self, client, session, landlord_1_token, test_tenancy_1):
        """Test successful update of tenancy details."""
        # Update data
        payload = {
            "rent_due": 1200.00,
            "lease_start_date": "2024-02-01",
            "lease_end_date": "2025-01-31"
        }
        headers = {"Authorization": f"Bearer {landlord_1_token}"}

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

    def test_update_tenancy_partial(self, client, session, landlord_1_token, test_tenancy_1):
        """Test partial update of tenancy details."""
        # Update only rent_due
        payload = {
            "rent_due": 1200.00
        }
        headers = {"Authorization": f"Bearer {landlord_1_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 200
        assert float(response.json["rent_due"]) == 1200.00
        assert response.json["lease_start_date"] == "2024-01-01"  # Unchanged
        assert response.json["lease_end_date"] == "2024-12-31"    # Unchanged

    def test_update_tenancy_remove_end_date(self, client, session, landlord_1_token, test_tenancy_1):
        """Test updating tenancy to remove end date."""
        # Set lease_end_date to null
        payload = {
            "lease_end_date": None
        }
        headers = {"Authorization": f"Bearer {landlord_1_token}"}

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

    def test_update_tenancy_invalid_dates(self, client, landlord_1_token, test_tenancy_1):
        """Test updating tenancy with invalid date format."""
        # Invalid date format
        payload = {
            "lease_start_date": "01-01-2024"  # Wrong format
        }
        headers = {"Authorization": f"Bearer {landlord_1_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 400
        assert "Invalid lease_start_date format" in response.json["error"]

    def test_update_tenancy_end_before_start(self, client, landlord_1_token, test_tenancy_1):
        """Test updating tenancy with end date before start date."""
        # End date before start date
        payload = {
            "lease_start_date": "2024-02-01",
            "lease_end_date": "2024-01-01"
        }
        headers = {"Authorization": f"Bearer {landlord_1_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Lease end date cannot be before start date"

    def test_update_tenancy_not_found(self, client, landlord_1_token):
        """Test updating non-existent tenancy."""
        payload = {
            "rent_due": 1200.00
        }
        headers = {"Authorization": f"Bearer {landlord_1_token}"}

        response = client.put(
            "/api/tenancies/999",  # Non-existent ID
            json=payload,
            headers=headers
        )

        assert response.status_code == 404
        assert response.json["error"] == "Tenancy not found"

    def test_update_tenancy_unauthorized_role(self, client, tenant_1_token, test_tenancy_1):
        """Test updating tenancy with unauthorized role (tenant)."""
        payload = {
            "rent_due": 1200.00
        }
        headers = {"Authorization": f"Bearer {tenant_1_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 403
        assert response.json["error"] == "Unauthorized"

    def test_update_tenancy_unauthorized_landlord(self, client, landlord_2_token, test_tenancy_1):
        """Test updating tenancy by a different landlord."""
        # Create token for different landlord

        payload = {
            "rent_due": 1200.00
        }
        headers = {"Authorization": f"Bearer {landlord_2_token}"}

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

    def test_update_tenancy_invalid_rent(self, client, landlord_1_token, test_tenancy_1):
        """Test updating tenancy with invalid rent value."""
        payload = {
            "rent_due": "invalid"
        }
        headers = {"Authorization": f"Bearer {landlord_1_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Invalid rent_due value"

    def test_update_tenancy_empty_payload(self, client, landlord_1_token, test_tenancy_1):
        """Test updating tenancy with empty payload."""
        payload = {}
        headers = {"Authorization": f"Bearer {landlord_1_token}"}

        response = client.put(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "No update data provided"


class TestGetTenancy:
    """Tests for GET /api/tenancies/<tenancy_id> endpoint."""

    def test_get_tenancy_success_landlord(self, client, landlord_1_token, test_tenancy_1):
        """Test successful retrieval of tenancy details by landlord."""
        headers = {"Authorization": f"Bearer {landlord_1_token}"}

        response = client.get(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            headers=headers
        )

        assert response.status_code == 200
        assert response.json["tenancy_id"] == test_tenancy_1.tenancy_id
        assert response.json["property_id"] == test_tenancy_1.property_id
        assert float(response.json["rent_due"]) == 1000.00
        assert response.json["lease_start_date"] == "2024-01-01"
        assert response.json["lease_end_date"] == "2024-12-31"
        assert "group_chat" in response.json
        assert response.json["group_chat"]["name"] == "Test Chat 1"

    def test_get_tenancy_success_tenant(self, client, tenant_1_token, test_tenancyTenants_1):
        """Test successful retrieval of tenancy details by associated tenant."""
        headers = {"Authorization": f"Bearer {tenant_1_token}"}

        response = client.get(
            f"/api/tenancies/{test_tenancyTenants_1.tenancy_id}",
            headers=headers
        )

        assert response.status_code == 200
        assert response.json["tenancy_id"] == test_tenancyTenants_1.tenancy_id

    def test_get_tenancy_not_found(self, client, landlord_1_token):
        """Test retrieval of non-existent tenancy."""
        headers = {"Authorization": f"Bearer {landlord_1_token}"}

        response = client.get(
            "/api/tenancies/999",  # Non-existent ID
            headers=headers
        )

        assert response.status_code == 404
        assert response.json["error"] == "Tenancy not found"

    def test_get_tenancy_unauthorized_tenant(self, client, tenant_1_token, test_tenancy_1):
        """Test retrieval by unauthorized tenant (not associated with tenancy)."""
        headers = {"Authorization": f"Bearer {tenant_1_token}"}

        response = client.get(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            headers=headers
        )

        assert response.status_code == 403
        assert response.json["error"] == "Unauthorized access to tenancy"

    def test_get_tenancy_unauthorized_landlord(self, client, landlord_2_token, test_tenancy_1):
        """Test retrieval by unauthorized landlord (doesn't own property)."""

        headers = {"Authorization": f"Bearer {landlord_2_token}"}

        response = client.get(
            f"/api/tenancies/{test_tenancy_1.tenancy_id}",
            headers=headers
        )

        assert response.status_code == 403
        assert response.json["error"] == "Unauthorized access to tenancy"

    def test_get_tenancy_no_token(self, client, test_tenancy_1):
        """Test retrieval without authentication token."""
        response = client.get(f"/api/tenancies/{test_tenancy_1.tenancy_id}")

        assert response.status_code == 401
        assert response.json["msg"] == "Missing Authorization Header"