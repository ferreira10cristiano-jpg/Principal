"""
Iteration 20 Backend Tests - Credits Tab Upgrade
Tests for:
- GET /api/network returns network_stats with level1/2/3/establishments
- GET /api/media returns public media assets
- POST /api/admin/media creates new media asset
- DELETE /api/admin/media/{id} removes media asset
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://draft-offer-mode.preview.emergentagent.com')
if not BASE_URL.endswith('/api'):
    BASE_URL = BASE_URL.rstrip('/') + '/api'

# Test credentials
CLIENT_EMAIL = "cliente@teste.com"
CLIENT_NAME = "Cliente Teste"
ADMIN_EMAIL = "admin@itoke.master"
ADMIN_NAME = "Admin iToke"


class TestNetworkEndpoint:
    """Test /api/network endpoint returns network_stats structure"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as client before each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as client
        login_response = self.session.post(f"{BASE_URL}/auth/email-login", json={
            "email": CLIENT_EMAIL,
            "name": CLIENT_NAME,
            "role": "client"
        })
        assert login_response.status_code == 200, f"Client login failed: {login_response.text}"
        data = login_response.json()
        self.session_token = data.get("session_token")
        self.session.headers.update({"Authorization": f"Bearer {self.session_token}"})
    
    def test_network_returns_network_stats(self):
        """GET /api/network should return network_stats with level1/2/3/establishments"""
        response = self.session.get(f"{BASE_URL}/network")
        assert response.status_code == 200, f"Network endpoint failed: {response.text}"
        
        data = response.json()
        
        # Verify network_stats exists
        assert "network_stats" in data, "Response missing 'network_stats' field"
        stats = data["network_stats"]
        
        # Verify level1 structure
        assert "level1" in stats, "network_stats missing 'level1'"
        assert "total" in stats["level1"], "level1 missing 'total'"
        assert "active" in stats["level1"], "level1 missing 'active'"
        assert "credits" in stats["level1"], "level1 missing 'credits'"
        
        # Verify level2 structure
        assert "level2" in stats, "network_stats missing 'level2'"
        assert "total" in stats["level2"], "level2 missing 'total'"
        assert "active" in stats["level2"], "level2 missing 'active'"
        assert "credits" in stats["level2"], "level2 missing 'credits'"
        
        # Verify level3 structure
        assert "level3" in stats, "network_stats missing 'level3'"
        assert "total" in stats["level3"], "level3 missing 'total'"
        assert "active" in stats["level3"], "level3 missing 'active'"
        assert "credits" in stats["level3"], "level3 missing 'credits'"
        
        # Verify establishments structure
        assert "establishments" in stats, "network_stats missing 'establishments'"
        assert "total" in stats["establishments"], "establishments missing 'total'"
        assert "active" in stats["establishments"], "establishments missing 'active'"
        assert "credits" in stats["establishments"], "establishments missing 'credits'"
        
        print(f"✓ Network stats structure verified: {stats}")
    
    def test_network_returns_referral_code(self):
        """GET /api/network should return referral_code"""
        response = self.session.get(f"{BASE_URL}/network")
        assert response.status_code == 200
        
        data = response.json()
        assert "referral_code" in data, "Response missing 'referral_code'"
        assert data["referral_code"] is not None, "referral_code is None"
        print(f"✓ Referral code: {data['referral_code']}")


class TestMediaEndpoints:
    """Test /api/media and /api/admin/media endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup sessions for client and admin"""
        self.client_session = requests.Session()
        self.client_session.headers.update({"Content-Type": "application/json"})
        
        self.admin_session = requests.Session()
        self.admin_session.headers.update({"Content-Type": "application/json"})
        
        # Login as client
        client_login = self.client_session.post(f"{BASE_URL}/auth/email-login", json={
            "email": CLIENT_EMAIL,
            "name": CLIENT_NAME,
            "role": "client"
        })
        assert client_login.status_code == 200, f"Client login failed: {client_login.text}"
        client_data = client_login.json()
        self.client_session.headers.update({"Authorization": f"Bearer {client_data['session_token']}"})
        
        # Login as admin
        admin_login = self.admin_session.post(f"{BASE_URL}/auth/email-login", json={
            "email": ADMIN_EMAIL,
            "name": ADMIN_NAME,
            "role": "admin"
        })
        assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
        admin_data = admin_login.json()
        self.admin_session.headers.update({"Authorization": f"Bearer {admin_data['session_token']}"})
    
    def test_get_public_media(self):
        """GET /api/media should return list of media assets"""
        response = self.client_session.get(f"{BASE_URL}/media")
        assert response.status_code == 200, f"Get public media failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Public media count: {len(data)}")
        
        # If there are media assets, verify structure
        if len(data) > 0:
            media = data[0]
            assert "media_id" in media, "Media missing 'media_id'"
            assert "url" in media, "Media missing 'url'"
            assert "title" in media, "Media missing 'title'"
            assert "type" in media, "Media missing 'type'"
            print(f"✓ First media: {media.get('title')} ({media.get('type')})")
    
    def test_get_admin_media(self):
        """GET /api/admin/media should return list of media assets for admin"""
        response = self.admin_session.get(f"{BASE_URL}/admin/media")
        assert response.status_code == 200, f"Get admin media failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Admin media count: {len(data)}")
    
    def test_admin_media_crud(self):
        """Test full CRUD cycle for admin media"""
        # CREATE - Add new media
        test_media = {
            "url": "https://example.com/test-image-iteration20.jpg",
            "title": "TEST_Iteration20_Media",
            "type": "image"
        }
        
        create_response = self.admin_session.post(f"{BASE_URL}/admin/media", json=test_media)
        assert create_response.status_code == 200, f"Create media failed: {create_response.text}"
        
        created = create_response.json()
        assert "media_id" in created, "Created media missing 'media_id'"
        assert created["title"] == test_media["title"], "Title mismatch"
        assert created["url"] == test_media["url"], "URL mismatch"
        assert created["type"] == test_media["type"], "Type mismatch"
        
        media_id = created["media_id"]
        print(f"✓ Created media: {media_id}")
        
        # READ - Verify it appears in list
        list_response = self.admin_session.get(f"{BASE_URL}/admin/media")
        assert list_response.status_code == 200
        media_list = list_response.json()
        found = any(m.get("media_id") == media_id for m in media_list)
        assert found, f"Created media {media_id} not found in list"
        print(f"✓ Media found in list")
        
        # DELETE - Remove the test media
        delete_response = self.admin_session.delete(f"{BASE_URL}/admin/media/{media_id}")
        assert delete_response.status_code == 200, f"Delete media failed: {delete_response.text}"
        print(f"✓ Deleted media: {media_id}")
        
        # VERIFY DELETE - Should not appear in list
        verify_response = self.admin_session.get(f"{BASE_URL}/admin/media")
        assert verify_response.status_code == 200
        verify_list = verify_response.json()
        still_exists = any(m.get("media_id") == media_id for m in verify_list)
        assert not still_exists, f"Media {media_id} still exists after delete"
        print(f"✓ Media deletion verified")


class TestAdminDashboardTabs:
    """Test that admin has access to required endpoints for 5 tabs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/auth/email-login", json={
            "email": ADMIN_EMAIL,
            "name": ADMIN_NAME,
            "role": "admin"
        })
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        data = login_response.json()
        self.session.headers.update({"Authorization": f"Bearer {data['session_token']}"})
    
    def test_admin_stats_endpoint(self):
        """GET /api/admin/stats for Geral tab"""
        response = self.session.get(f"{BASE_URL}/admin/stats")
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        data = response.json()
        assert "total_users" in data, "Missing total_users"
        print(f"✓ Admin stats: {data.get('total_users')} users")
    
    def test_admin_financial_endpoint(self):
        """GET /api/admin/financial for Financ. tab"""
        response = self.session.get(f"{BASE_URL}/admin/financial")
        assert response.status_code == 200, f"Admin financial failed: {response.text}"
        print(f"✓ Admin financial endpoint working")
    
    def test_admin_withdrawals_endpoint(self):
        """GET /api/admin/withdrawals for Saques tab"""
        response = self.session.get(f"{BASE_URL}/admin/withdrawals")
        assert response.status_code == 200, f"Admin withdrawals failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Withdrawals should be a list"
        print(f"✓ Admin withdrawals: {len(data)} pending")
    
    def test_admin_users_endpoint(self):
        """GET /api/admin/users for Usuarios tab"""
        response = self.session.get(f"{BASE_URL}/admin/users")
        assert response.status_code == 200, f"Admin users failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Users should be a list"
        print(f"✓ Admin users: {len(data)} users")
    
    def test_admin_media_endpoint(self):
        """GET /api/admin/media for Midias tab"""
        response = self.session.get(f"{BASE_URL}/admin/media")
        assert response.status_code == 200, f"Admin media failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Media should be a list"
        print(f"✓ Admin media: {len(data)} assets")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
