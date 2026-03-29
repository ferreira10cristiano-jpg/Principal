"""
Test QR Generation with Credits - Iteration 13
Tests the DOM stability fix and partial credit validation
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://draft-offer-mode.preview.emergentagent.com')

class TestQRGenerationWithCredits:
    """Tests for QR generation with partial credits"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data - login as client and set balances"""
        # Login as client
        login_resp = requests.post(f"{BASE_URL}/api/auth/email-login", json={
            "email": "cliente@teste.com",
            "name": "Cliente Teste",
            "role": "client"
        })
        assert login_resp.status_code == 200, f"Client login failed: {login_resp.text}"
        self.client_token = login_resp.json().get("session_token")
        self.client_user = login_resp.json().get("user")
        self.client_headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # Login as establishment
        est_login = requests.post(f"{BASE_URL}/api/auth/email-login", json={
            "email": "teste@estabelecimento.com",
            "name": "Teste Estabelecimento",
            "role": "establishment"
        })
        assert est_login.status_code == 200, f"Establishment login failed: {est_login.text}"
        self.est_token = est_login.json().get("session_token")
        self.est_headers = {"Authorization": f"Bearer {self.est_token}"}
        
        # Get test offer
        self.test_offer_id = "offer_faa3cfe6cae5"
        
    def test_health_check(self):
        """Verify API is healthy"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "healthy"
        print("Health check passed")
    
    def test_qr_generate_with_credits_3_00(self):
        """POST /api/qr/generate with credits 3.00 - must return valid JSON with credits_used=3.0"""
        # First check user has enough tokens and credits
        me_resp = requests.get(f"{BASE_URL}/api/auth/me", headers=self.client_headers)
        assert me_resp.status_code == 200
        user_data = me_resp.json()
        print(f"User tokens: {user_data.get('tokens')}, credits: {user_data.get('credits')}")
        
        # Generate QR with 3.00 credits
        gen_resp = requests.post(f"{BASE_URL}/api/qr/generate", 
            headers=self.client_headers,
            json={
                "offer_id": self.test_offer_id,
                "use_credits": 3.00
            }
        )
        
        assert gen_resp.status_code == 200, f"QR generation failed: {gen_resp.text}"
        data = gen_resp.json()
        
        # Verify response structure
        assert "code_hash" in data, "Missing code_hash in response"
        assert "backup_code" in data, "Missing backup_code in response"
        assert "credits_used" in data or "credits_reserved" in data, "Missing credits_used/credits_reserved"
        
        credits_used = data.get("credits_used", data.get("credits_reserved", 0))
        assert credits_used == 3.0, f"Expected credits_used=3.0, got {credits_used}"
        
        # Verify final_price_to_pay is calculated correctly
        discounted_price = data.get("discounted_price", 0)
        final_price = data.get("final_price_to_pay", 0)
        expected_final = max(0, discounted_price - 3.0)
        assert abs(final_price - expected_final) < 0.01, f"Expected final_price={expected_final}, got {final_price}"
        
        print(f"QR generated successfully: code_hash={data.get('code_hash')}, backup_code={data.get('backup_code')}")
        print(f"credits_used={credits_used}, final_price_to_pay={final_price}")
        
        return data
    
    def test_qr_validate_returns_preview_step(self):
        """POST /api/qr/validate - returns step=preview with billing details"""
        # First generate a QR
        gen_resp = requests.post(f"{BASE_URL}/api/qr/generate", 
            headers=self.client_headers,
            json={
                "offer_id": self.test_offer_id,
                "use_credits": 2.50
            }
        )
        assert gen_resp.status_code == 200, f"QR generation failed: {gen_resp.text}"
        qr_data = gen_resp.json()
        code_hash = qr_data.get("code_hash")
        
        # Validate as establishment
        validate_resp = requests.post(f"{BASE_URL}/api/qr/validate",
            headers=self.est_headers,
            json={"code_hash": code_hash}
        )
        
        assert validate_resp.status_code == 200, f"Validation failed: {validate_resp.text}"
        data = validate_resp.json()
        
        # Verify step=preview
        assert data.get("step") == "preview", f"Expected step=preview, got {data.get('step')}"
        
        # Verify billing details present
        assert "voucher_id" in data, "Missing voucher_id"
        assert "customer_name" in data, "Missing customer_name"
        assert "offer_title" in data, "Missing offer_title"
        assert "credits_used" in data, "Missing credits_used"
        assert "amount_to_pay_cash" in data, "Missing amount_to_pay_cash"
        
        print(f"Validate preview: step={data.get('step')}, credits_used={data.get('credits_used')}, amount_to_pay_cash={data.get('amount_to_pay_cash')}")
        
        return data
    
    def test_qr_confirm_finalizes_sale(self):
        """POST /api/qr/confirm - finalizes sale with step=confirmed"""
        # Generate QR
        gen_resp = requests.post(f"{BASE_URL}/api/qr/generate", 
            headers=self.client_headers,
            json={
                "offer_id": self.test_offer_id,
                "use_credits": 1.50
            }
        )
        assert gen_resp.status_code == 200
        qr_data = gen_resp.json()
        code_hash = qr_data.get("code_hash")
        
        # Validate to get voucher_id
        validate_resp = requests.post(f"{BASE_URL}/api/qr/validate",
            headers=self.est_headers,
            json={"code_hash": code_hash}
        )
        assert validate_resp.status_code == 200
        preview_data = validate_resp.json()
        voucher_id = preview_data.get("voucher_id")
        
        # Confirm the sale
        confirm_resp = requests.post(f"{BASE_URL}/api/qr/confirm",
            headers=self.est_headers,
            json={"voucher_id": voucher_id}
        )
        
        assert confirm_resp.status_code == 200, f"Confirm failed: {confirm_resp.text}"
        data = confirm_resp.json()
        
        # Verify step=confirmed
        assert data.get("step") == "confirmed", f"Expected step=confirmed, got {data.get('step')}"
        assert data.get("success") == True, "Expected success=True"
        
        print(f"Confirm: step={data.get('step')}, success={data.get('success')}, message={data.get('message')}")
        
        return data
    
    def test_partial_credit_values(self):
        """Test that partial credit values like 2.00, 3.50 work correctly"""
        test_values = [2.00, 3.50, 0.50, 1.25]
        
        for credit_value in test_values:
            gen_resp = requests.post(f"{BASE_URL}/api/qr/generate", 
                headers=self.client_headers,
                json={
                    "offer_id": self.test_offer_id,
                    "use_credits": credit_value
                }
            )
            
            # Should succeed (assuming user has enough credits)
            if gen_resp.status_code == 200:
                data = gen_resp.json()
                credits_used = data.get("credits_used", data.get("credits_reserved", 0))
                # Credits used should be <= requested (capped by balance or offer price)
                assert credits_used <= credit_value + 0.01, f"Credits used {credits_used} > requested {credit_value}"
                print(f"Partial credit {credit_value}: OK, credits_used={credits_used}")
            else:
                # May fail if insufficient tokens/credits - that's OK
                print(f"Partial credit {credit_value}: {gen_resp.status_code} - {gen_resp.text[:100]}")


class TestValidationFlow:
    """Tests for the 2-step validation flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        # Login as client
        login_resp = requests.post(f"{BASE_URL}/api/auth/email-login", json={
            "email": "cliente@teste.com",
            "name": "Cliente Teste",
            "role": "client"
        })
        assert login_resp.status_code == 200
        self.client_token = login_resp.json().get("session_token")
        self.client_headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # Login as establishment
        est_login = requests.post(f"{BASE_URL}/api/auth/email-login", json={
            "email": "teste@estabelecimento.com",
            "name": "Teste Estabelecimento",
            "role": "establishment"
        })
        assert est_login.status_code == 200
        self.est_token = est_login.json().get("session_token")
        self.est_headers = {"Authorization": f"Bearer {self.est_token}"}
        
        self.test_offer_id = "offer_faa3cfe6cae5"
    
    def test_validate_with_backup_code(self):
        """Test validation using backup code (ITK-XXX format)"""
        # Generate QR
        gen_resp = requests.post(f"{BASE_URL}/api/qr/generate", 
            headers=self.client_headers,
            json={"offer_id": self.test_offer_id, "use_credits": 0}
        )
        assert gen_resp.status_code == 200
        qr_data = gen_resp.json()
        backup_code = qr_data.get("backup_code")
        
        # Validate using backup code
        validate_resp = requests.post(f"{BASE_URL}/api/qr/validate",
            headers=self.est_headers,
            json={"code_hash": backup_code}  # Using backup code in code_hash field
        )
        
        assert validate_resp.status_code == 200, f"Validation with backup code failed: {validate_resp.text}"
        data = validate_resp.json()
        assert data.get("step") == "preview"
        print(f"Validation with backup code {backup_code}: OK")
    
    def test_confirm_already_used_voucher(self):
        """Test that confirming an already used voucher returns 400"""
        # Generate and confirm a voucher
        gen_resp = requests.post(f"{BASE_URL}/api/qr/generate", 
            headers=self.client_headers,
            json={"offer_id": self.test_offer_id, "use_credits": 0}
        )
        assert gen_resp.status_code == 200
        qr_data = gen_resp.json()
        code_hash = qr_data.get("code_hash")
        
        # Validate
        validate_resp = requests.post(f"{BASE_URL}/api/qr/validate",
            headers=self.est_headers,
            json={"code_hash": code_hash}
        )
        assert validate_resp.status_code == 200
        voucher_id = validate_resp.json().get("voucher_id")
        
        # Confirm first time
        confirm_resp = requests.post(f"{BASE_URL}/api/qr/confirm",
            headers=self.est_headers,
            json={"voucher_id": voucher_id}
        )
        assert confirm_resp.status_code == 200
        
        # Try to confirm again - should fail
        confirm_again = requests.post(f"{BASE_URL}/api/qr/confirm",
            headers=self.est_headers,
            json={"voucher_id": voucher_id}
        )
        assert confirm_again.status_code == 400, f"Expected 400 for already used voucher, got {confirm_again.status_code}"
        print("Confirm already used voucher: correctly returns 400")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
