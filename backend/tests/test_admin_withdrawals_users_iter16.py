"""
Test Admin Withdrawals and Users endpoints - Iteration 16
Tests for:
- GET /api/admin/withdrawals - list establishments with withdrawable_balance > 0
- POST /api/admin/withdrawals/approve - approve withdrawal, deduct balance, create audit log
- GET /api/admin/users - list all users with user_id, name, email, role, blocked
- PUT /api/admin/users/{user_id}/block - toggle blocked status
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://draft-offer-mode.preview.emergentagent.com')

class TestAdminWithdrawals:
    """Tests for admin withdrawal management endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin session for tests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_resp = self.session.post(f"{BASE_URL}/api/auth/email-login", json={
            "email": "admin@itoke.master",
            "name": "Admin iToke",
            "role": "admin"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        data = login_resp.json()
        self.admin_token = data.get("session_token")
        self.admin_user = data.get("user")
        self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        
        # Also create a client session for non-admin tests
        self.client_session = requests.Session()
        self.client_session.headers.update({"Content-Type": "application/json"})
        client_login = self.client_session.post(f"{BASE_URL}/api/auth/email-login", json={
            "email": "cliente@teste.com",
            "name": "Cliente Teste",
            "role": "client"
        })
        if client_login.status_code == 200:
            client_data = client_login.json()
            self.client_token = client_data.get("session_token")
            self.client_session.headers.update({"Authorization": f"Bearer {self.client_token}"})
        
        yield
    
    def test_get_withdrawals_returns_list(self):
        """GET /api/admin/withdrawals returns list of establishments with balance > 0"""
        response = self.session.get(f"{BASE_URL}/api/admin/withdrawals")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # Each item should have required fields
        for item in data:
            assert "establishment_id" in item, "Missing establishment_id"
            assert "name" in item, "Missing name (business_name)"
            assert "withdrawable_balance" in item, "Missing withdrawable_balance"
            assert "pix_key" in item, "Missing pix_key field"
            # Balance should be > 0
            assert item["withdrawable_balance"] > 0, f"Balance should be > 0, got {item['withdrawable_balance']}"
        
        print(f"Found {len(data)} establishments with withdrawable balance")
    
    def test_get_withdrawals_rejects_non_admin(self):
        """GET /api/admin/withdrawals rejects non-admin users with 403"""
        response = self.client_session.get(f"{BASE_URL}/api/admin/withdrawals")
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
    
    def test_get_withdrawals_rejects_unauthenticated(self):
        """GET /api/admin/withdrawals rejects unauthenticated requests with 401"""
        no_auth_session = requests.Session()
        response = no_auth_session.get(f"{BASE_URL}/api/admin/withdrawals")
        assert response.status_code == 401, f"Expected 401 for unauthenticated, got {response.status_code}"
    
    def test_approve_withdrawal_success(self):
        """POST /api/admin/withdrawals/approve deducts balance and creates records"""
        # First get list of establishments with balance
        list_resp = self.session.get(f"{BASE_URL}/api/admin/withdrawals")
        assert list_resp.status_code == 200
        establishments = list_resp.json()
        
        if len(establishments) == 0:
            pytest.skip("No establishments with withdrawable balance to test")
        
        # Pick first establishment and approve a small amount (R$1.00)
        est = establishments[0]
        est_id = est["establishment_id"]
        original_balance = est["withdrawable_balance"]
        approve_amount = min(1.00, original_balance)  # Approve R$1 or less
        
        response = self.session.post(f"{BASE_URL}/api/admin/withdrawals/approve", json={
            "establishment_id": est_id,
            "amount": approve_amount
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "withdrawal_id" in data, "Response should contain withdrawal_id"
        assert "amount" in data, "Response should contain amount"
        assert "new_balance" in data, "Response should contain new_balance"
        assert data["amount"] == approve_amount, f"Amount mismatch: expected {approve_amount}, got {data['amount']}"
        assert data["new_balance"] == original_balance - approve_amount, "New balance calculation incorrect"
        
        print(f"Approved withdrawal of R${approve_amount} for {est['name']}, new balance: R${data['new_balance']}")
    
    def test_approve_withdrawal_rejects_amount_greater_than_balance(self):
        """POST /api/admin/withdrawals/approve rejects if amount > balance"""
        # Get an establishment
        list_resp = self.session.get(f"{BASE_URL}/api/admin/withdrawals")
        if list_resp.status_code != 200 or len(list_resp.json()) == 0:
            pytest.skip("No establishments with balance to test")
        
        est = list_resp.json()[0]
        est_id = est["establishment_id"]
        balance = est["withdrawable_balance"]
        
        # Try to approve more than available
        response = self.session.post(f"{BASE_URL}/api/admin/withdrawals/approve", json={
            "establishment_id": est_id,
            "amount": balance + 1000  # Way more than available
        })
        assert response.status_code == 400, f"Expected 400 for amount > balance, got {response.status_code}"
    
    def test_approve_withdrawal_rejects_non_admin(self):
        """POST /api/admin/withdrawals/approve rejects non-admin users"""
        response = self.client_session.post(f"{BASE_URL}/api/admin/withdrawals/approve", json={
            "establishment_id": "est_test",
            "amount": 10.00
        })
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
    
    def test_approve_withdrawal_rejects_invalid_establishment(self):
        """POST /api/admin/withdrawals/approve rejects non-existent establishment"""
        response = self.session.post(f"{BASE_URL}/api/admin/withdrawals/approve", json={
            "establishment_id": "est_nonexistent_12345",
            "amount": 10.00
        })
        assert response.status_code == 404, f"Expected 404 for invalid establishment, got {response.status_code}"
    
    def test_approve_withdrawal_rejects_zero_amount(self):
        """POST /api/admin/withdrawals/approve rejects zero or negative amount"""
        list_resp = self.session.get(f"{BASE_URL}/api/admin/withdrawals")
        if list_resp.status_code != 200 or len(list_resp.json()) == 0:
            pytest.skip("No establishments with balance to test")
        
        est = list_resp.json()[0]
        
        response = self.session.post(f"{BASE_URL}/api/admin/withdrawals/approve", json={
            "establishment_id": est["establishment_id"],
            "amount": 0
        })
        assert response.status_code == 400, f"Expected 400 for zero amount, got {response.status_code}"


class TestAdminUsers:
    """Tests for admin user management endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin session for tests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_resp = self.session.post(f"{BASE_URL}/api/auth/email-login", json={
            "email": "admin@itoke.master",
            "name": "Admin iToke",
            "role": "admin"
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        data = login_resp.json()
        self.admin_token = data.get("session_token")
        self.admin_user = data.get("user")
        self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        
        # Also create a client session for non-admin tests
        self.client_session = requests.Session()
        self.client_session.headers.update({"Content-Type": "application/json"})
        client_login = self.client_session.post(f"{BASE_URL}/api/auth/email-login", json={
            "email": "cliente@teste.com",
            "name": "Cliente Teste",
            "role": "client"
        })
        if client_login.status_code == 200:
            client_data = client_login.json()
            self.client_token = client_data.get("session_token")
            self.client_user = client_data.get("user")
            self.client_session.headers.update({"Authorization": f"Bearer {self.client_token}"})
        
        yield
    
    def test_get_users_returns_list(self):
        """GET /api/admin/users returns all users with required fields"""
        response = self.session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one user"
        
        # Each user should have required fields
        for user in data:
            assert "user_id" in user, "Missing user_id"
            assert "name" in user, "Missing name"
            assert "email" in user, "Missing email"
            assert "role" in user, "Missing role"
            assert "blocked" in user, "Missing blocked field"
            # blocked should be boolean
            assert isinstance(user["blocked"], bool), f"blocked should be boolean, got {type(user['blocked'])}"
        
        print(f"Found {len(data)} users total")
        
        # Count by role
        roles = {}
        for u in data:
            role = u.get("role", "unknown")
            roles[role] = roles.get(role, 0) + 1
        print(f"Users by role: {roles}")
    
    def test_get_users_rejects_non_admin(self):
        """GET /api/admin/users rejects non-admin users with 403"""
        response = self.client_session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
    
    def test_get_users_rejects_unauthenticated(self):
        """GET /api/admin/users rejects unauthenticated requests with 401"""
        no_auth_session = requests.Session()
        response = no_auth_session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 401, f"Expected 401 for unauthenticated, got {response.status_code}"
    
    def test_block_user_success(self):
        """PUT /api/admin/users/{user_id}/block toggles blocked status"""
        # Get a non-admin user to block
        users_resp = self.session.get(f"{BASE_URL}/api/admin/users")
        assert users_resp.status_code == 200
        users = users_resp.json()
        
        # Find a non-admin user
        target_user = None
        for u in users:
            if u.get("role") != "admin":
                target_user = u
                break
        
        if not target_user:
            pytest.skip("No non-admin users to test blocking")
        
        user_id = target_user["user_id"]
        current_blocked = target_user.get("blocked", False)
        
        # Toggle block status
        response = self.session.put(f"{BASE_URL}/api/admin/users/{user_id}/block", json={
            "blocked": not current_blocked
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "blocked" in data, "Response should contain blocked status"
        assert data["blocked"] == (not current_blocked), "Blocked status should be toggled"
        
        # Revert the change
        revert_resp = self.session.put(f"{BASE_URL}/api/admin/users/{user_id}/block", json={
            "blocked": current_blocked
        })
        assert revert_resp.status_code == 200, "Failed to revert block status"
        
        print(f"Successfully toggled block status for user {user_id}")
    
    def test_block_admin_user_rejected(self):
        """PUT /api/admin/users/{user_id}/block cannot block admin users"""
        # Get admin user
        users_resp = self.session.get(f"{BASE_URL}/api/admin/users")
        assert users_resp.status_code == 200
        users = users_resp.json()
        
        # Find an admin user
        admin_user = None
        for u in users:
            if u.get("role") == "admin":
                admin_user = u
                break
        
        if not admin_user:
            pytest.skip("No admin users found to test")
        
        # Try to block admin
        response = self.session.put(f"{BASE_URL}/api/admin/users/{admin_user['user_id']}/block", json={
            "blocked": True
        })
        assert response.status_code == 400, f"Expected 400 when blocking admin, got {response.status_code}"
        
        print("Correctly rejected attempt to block admin user")
    
    def test_block_user_rejects_non_admin(self):
        """PUT /api/admin/users/{user_id}/block rejects non-admin users"""
        response = self.client_session.put(f"{BASE_URL}/api/admin/users/some_user_id/block", json={
            "blocked": True
        })
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
    
    def test_block_nonexistent_user(self):
        """PUT /api/admin/users/{user_id}/block returns 404 for non-existent user"""
        response = self.session.put(f"{BASE_URL}/api/admin/users/user_nonexistent_12345/block", json={
            "blocked": True
        })
        assert response.status_code == 404, f"Expected 404 for non-existent user, got {response.status_code}"


class TestHealthCheck:
    """Basic health check"""
    
    def test_health_endpoint(self):
        """Health check endpoint works"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("Health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
