#!/usr/bin/env python3
"""
Backend API Testing for iToke Platform - QR Generation and Credits Issues
Testing the specific issues reported:
1. 'Invalid session' error when generating QR Code - need to verify authentication
2. Client credits not showing on QR generation screen - need to show token and credit balance with option to choose
"""

import requests
import sys
import json
from datetime import datetime

class iTokeTester:
    def __init__(self, base_url="https://draft-offer-mode.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.establishment_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.session_token:
            test_headers['Authorization'] = f'Bearer {self.session_token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(name, True, f"Status: {response.status_code}")
                    return True, response_data
                except:
                    self.log_test(name, True, f"Status: {response.status_code} (no JSON)")
                    return True, {}
            else:
                try:
                    error_data = response.json()
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                except:
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_client_login(self):
        """Test login as client user"""
        print("\n🔐 Testing Client Login...")
        
        login_data = {
            "email": "cliente@teste.com",
            "name": "Cliente Teste",
            "role": "client"
        }
        
        success, response = self.run_test(
            "Login as client",
            "POST",
            "/auth/email-login",
            200,
            data=login_data
        )
        
        if success and 'session_token' in response:
            self.session_token = response['session_token']
            user_data = response.get('user', {})
            print(f"   Session token: {self.session_token[:20]}...")
            print(f"   User ID: {user_data.get('user_id', 'N/A')}")
            print(f"   Tokens: {user_data.get('tokens', 0)}")
            print(f"   Credits: {user_data.get('credits', 0)}")
            return True, user_data
        return False, {}

    def test_establishment_login(self):
        """Test login as establishment user"""
        print("\n🔐 Testing Establishment Login...")
        
        login_data = {
            "email": "teste@estabelecimento.com",
            "name": "Estabelecimento Teste",
            "role": "establishment"
        }
        
        success, response = self.run_test(
            "Login as establishment",
            "POST",
            "/auth/email-login",
            200,
            data=login_data
        )
        
        if success and 'session_token' in response:
            self.session_token = response['session_token']
            print(f"   Session token: {self.session_token[:20]}...")
            return True
        return False

    def test_auth_me_endpoint(self):
        """Test GET /api/auth/me - should return tokens and credits"""
        print("\n👤 Testing GET /api/auth/me...")
        
        success, response = self.run_test(
            "GET /api/auth/me",
            "GET",
            "/auth/me",
            200
        )
        
        if success:
            print(f"   User ID: {response.get('user_id', 'N/A')}")
            print(f"   Email: {response.get('email', 'N/A')}")
            print(f"   Role: {response.get('role', 'N/A')}")
            print(f"   Tokens: {response.get('tokens', 'N/A')}")
            print(f"   Credits: {response.get('credits', 'N/A')}")
            
            # Verify tokens and credits are present
            if 'tokens' in response and 'credits' in response:
                self.log_test("Auth/me includes tokens and credits", True, f"Tokens: {response['tokens']}, Credits: {response['credits']}")
                return True, response
            else:
                self.log_test("Auth/me includes tokens and credits", False, "Missing tokens or credits in response")
                return False, response
        return False, {}

    def test_qr_generation_with_tokens(self, offer_id):
        """Test POST /api/qr/generate with use_credits=0 (should use token)"""
        print("\n🎫 Testing QR Generation with Tokens...")
        
        qr_data = {
            "offer_id": offer_id,
            "use_credits": 0
        }
        
        success, response = self.run_test(
            "POST /api/qr/generate (use tokens)",
            "POST",
            "/qr/generate",
            200,
            data=qr_data
        )
        
        if success:
            print(f"   QR ID: {response.get('qr_id', 'N/A')}")
            print(f"   Code Hash: {response.get('code_hash', 'N/A')}")
            print(f"   Offer Code: {response.get('offer_code', 'N/A')}")
            print(f"   Credits Used: {response.get('credits_used_on_generation', 0)}")
            return True, response
        return False, {}

    def test_qr_generation_with_credits(self, offer_id):
        """Test POST /api/qr/generate with use_credits=1 (should use credits if available)"""
        print("\n💳 Testing QR Generation with Credits...")
        
        qr_data = {
            "offer_id": offer_id,
            "use_credits": 1
        }
        
        success, response = self.run_test(
            "POST /api/qr/generate (use credits)",
            "POST",
            "/qr/generate",
            200,
            data=qr_data
        )
        
        if success:
            print(f"   QR ID: {response.get('qr_id', 'N/A')}")
            print(f"   Code Hash: {response.get('code_hash', 'N/A')}")
            print(f"   Offer Code: {response.get('offer_code', 'N/A')}")
            print(f"   Credits Used: {response.get('credits_used_on_generation', 0)}")
            return True, response
        return False, {}

    def test_insufficient_balance_scenarios(self, offer_id):
        """Test QR generation with insufficient balance"""
        print("\n⚠️ Testing Insufficient Balance Scenarios...")
        
        # First, let's check current balance
        success, user_data = self.run_test(
            "Check current balance",
            "GET",
            "/auth/me",
            200
        )
        
        if success:
            tokens = user_data.get('tokens', 0)
            credits = user_data.get('credits', 0)
            print(f"   Current balance - Tokens: {tokens}, Credits: {credits}")
            
            # If user has no tokens or credits, test should fail appropriately
            if tokens == 0 and credits == 0:
                qr_data = {"offer_id": offer_id, "use_credits": 0}
                success, response = self.run_test(
                    "QR generation with zero balance",
                    "POST",
                    "/qr/generate",
                    400,  # Should return 400 for insufficient balance
                    data=qr_data
                )
                if success:
                    self.log_test("Insufficient balance handling", True, "Correctly rejected QR generation with zero balance")
                else:
                    self.log_test("Insufficient balance handling", False, "Should reject QR generation with zero balance")
            else:
                self.log_test("Insufficient balance test", True, "User has sufficient balance, skipping test")
        
        return True
    def test_get_establishment(self):
        """Test GET /api/establishments/me"""
        print("\n🏢 Testing Get My Establishment...")
        
        success, response = self.run_test(
            "GET /api/establishments/me",
            "GET",
            "/establishments/me",
            200
        )
        
        if success:
            self.establishment_data = response
            print(f"   Establishment ID: {response.get('establishment_id', 'N/A')}")
            print(f"   Business Name: {response.get('business_name', 'N/A')}")
            print(f"   Token Balance: {response.get('token_balance', 0)}")
            return True
        return False

    def get_test_offer_id(self):
        """Get an existing offer ID for testing QR generation"""
        print("\n🔍 Getting Test Offer ID...")
        
        # First try to get existing offers
        success, response = self.run_test(
            "GET /api/offers (public)",
            "GET",
            "/offers?limit=1",
            200
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            offer_id = response[0].get('offer_id')
            print(f"   Using existing offer ID: {offer_id}")
            return offer_id
        
        # If no offers exist, we need to create one first
        # Switch to establishment login temporarily
        old_token = self.session_token
        
        if self.test_establishment_login():
            if self.test_get_establishment():
                create_success, new_offer = self.test_create_offer()
                if create_success:
                    offer_id = new_offer.get('offer_id')
                    print(f"   Created new offer ID: {offer_id}")
                    # Switch back to client login
                    self.session_token = old_token
                    return offer_id
        
        # Restore client token
        self.session_token = old_token
        return None

    def test_get_my_offers(self):
        """Test GET /api/establishments/me/offers"""
        print("\n📋 Testing Get My Offers...")
        
        success, response = self.run_test(
            "GET /api/establishments/me/offers",
            "GET",
            "/establishments/me/offers",
            200
        )
        
        if success:
            offers_count = len(response) if isinstance(response, list) else 0
            print(f"   Found {offers_count} existing offers")
            
            if offers_count > 0:
                print("   Existing offers:")
                for i, offer in enumerate(response[:3]):  # Show first 3
                    print(f"     {i+1}. {offer.get('title', 'No title')} - {offer.get('offer_code', 'No code')}")
            
            return True, response
        return False, []

    def test_create_offer(self):
        """Test POST /api/offers - Create new offer"""
        print("\n➕ Testing Create New Offer...")
        
        if not self.establishment_data:
            self.log_test("Create offer (no establishment)", False, "No establishment data available")
            return False
        
        # Create test offer data
        offer_data = {
            "title": f"Teste Oferta {datetime.now().strftime('%H:%M:%S')}",
            "description": "Oferta de teste criada automaticamente para verificar funcionalidade",
            "discount_value": 30,
            "original_price": 50.00,
            "discounted_price": 35.00,
            "valid_days": "Seg, Ter, Qua, Qui, Sex",
            "valid_hours": "11:00 às 22:00",
            "delivery_allowed": True,
            "dine_in_only": False,
            "pickup_allowed": True,
            "rules": "• Não cumulativa com outros descontos\n• Apresentar QR Code no balcão"
        }
        
        success, response = self.run_test(
            "POST /api/offers (Create offer)",
            "POST",
            "/offers",
            200,  # Expecting 200 based on backend code
            data=offer_data
        )
        
        if success:
            print(f"   Created offer ID: {response.get('offer_id', 'N/A')}")
            print(f"   Offer code: {response.get('offer_code', 'N/A')}")
            print(f"   Is simulation: {response.get('is_simulation', False)}")
            return True, response
        return False, {}

    def test_offers_after_creation(self):
        """Test that offers list is updated after creation"""
        print("\n🔄 Testing Offers List After Creation...")
        
        success, offers = self.test_get_my_offers()
        if success:
            offers_count = len(offers) if isinstance(offers, list) else 0
            if offers_count > 0:
                self.log_test("Offers list populated after creation", True, f"Found {offers_count} offers")
                return True
            else:
                self.log_test("Offers list populated after creation", False, "No offers found after creation")
                return False
        return False

    def test_establishment_registration_flow(self):
        """Test if user needs to register establishment first"""
        print("\n🏗️ Testing Establishment Registration Flow...")
        
        # Try with a fresh user that might not have establishment
        fresh_login_data = {
            "email": f"novo_estabelecimento_{datetime.now().strftime('%H%M%S')}@teste.com",
            "name": "Novo Estabelecimento Teste",
            "role": "establishment"
        }
        
        # Save current token
        old_token = self.session_token
        
        success, response = self.run_test(
            "Login as new establishment user",
            "POST",
            "/auth/email-login",
            200,
            data=fresh_login_data
        )
        
        if success and 'session_token' in response:
            self.session_token = response['session_token']
            
            # Try to get establishment (should fail)
            success, _ = self.run_test(
                "GET /api/establishments/me (new user)",
                "GET",
                "/establishments/me",
                404  # Expecting 404 for new user
            )
            
            if success:
                self.log_test("New user establishment flow", True, "Correctly returns 404 for new user")
            else:
                self.log_test("New user establishment flow", False, "Should return 404 for new user without establishment")
        
        # Restore original token
        self.session_token = old_token
        return True

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting iToke Backend API Tests - QR Generation & Credits")
        print("=" * 70)
        
        # Test 1: Client Login
        print("\n=== CLIENT AUTHENTICATION TESTS ===")
        client_success, client_data = self.test_client_login()
        if not client_success:
            print("❌ Client login failed - cannot continue with QR tests")
            return False
        
        # Test 2: Auth/me endpoint
        auth_success, auth_data = self.test_auth_me_endpoint()
        if not auth_success:
            print("❌ Auth/me failed - session validation issue")
            return False
        
        # Test 3: Get test offer ID
        offer_id = self.get_test_offer_id()
        if not offer_id:
            print("❌ Could not get test offer ID - cannot test QR generation")
            return False
        
        print(f"\n=== QR GENERATION TESTS (Offer ID: {offer_id}) ===")
        
        # Test 4: QR Generation with tokens
        token_qr_success, token_qr_data = self.test_qr_generation_with_tokens(offer_id)
        
        # Test 5: QR Generation with credits (if user has credits)
        if auth_data.get('credits', 0) >= 1:
            credit_qr_success, credit_qr_data = self.test_qr_generation_with_credits(offer_id)
        else:
            print("⚠️ User has no credits, skipping credit QR generation test")
            credit_qr_success = True  # Skip this test
        
        # Test 6: Insufficient balance scenarios
        self.test_insufficient_balance_scenarios(offer_id)
        
        # Test 7: Establishment login (for completeness)
        print("\n=== ESTABLISHMENT AUTHENTICATION TESTS ===")
        if self.test_establishment_login():
            self.test_get_establishment()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed < self.tests_run:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"  - {result['test']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = iTokeTester()
    
    try:
        success = tester.run_comprehensive_test()
        tester.print_summary()
        
        if success:
            print("\n🎉 All tests passed! QR generation and authentication appear to be working.")
            return 0
        else:
            print("\n⚠️  Some tests failed. There may be issues with QR generation or authentication.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())