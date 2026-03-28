#!/usr/bin/env python3
"""
Backend API Testing for iToke Platform - Voucher System with Backup Codes
Testing the specific features implemented:
1. POST /api/qr/generate - deve retornar backup_code no formato ITK-XXX
2. POST /api/qr/generate - deve salvar em vouchers collection
3. GET /api/vouchers/my - deve retornar vouchers do cliente
4. POST /api/qr/validate com backup_code - deve validar corretamente
5. POST /api/qr/validate - deve retornar credits_used e amount_to_pay_cash
6. GET /api/establishments/me/sales-history - deve retornar histórico e sumário
"""

import requests
import sys
import json
import re
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

    def test_qr_generation_with_backup_code(self, offer_id):
        """Test POST /api/qr/generate - should return backup_code in ITK-XXX format"""
        print("\n🎫 Testing QR Generation with Backup Code...")
        
        qr_data = {
            "offer_id": offer_id,
            "use_credits": 0
        }
        
        success, response = self.run_test(
            "POST /api/qr/generate (backup code format)",
            "POST",
            "/qr/generate",
            200,
            data=qr_data
        )
        
        if success:
            backup_code = response.get('backup_code')
            print(f"   QR ID: {response.get('qr_id', 'N/A')}")
            print(f"   Code Hash: {response.get('code_hash', 'N/A')}")
            print(f"   Backup Code: {backup_code}")
            print(f"   Offer Code: {response.get('offer_code', 'N/A')}")
            
            # Verify backup code format ITK-XXX
            if backup_code and re.match(r'^ITK-[A-Z0-9]{3}$', backup_code):
                self.log_test("Backup code format ITK-XXX", True, f"Format correct: {backup_code}")
            else:
                self.log_test("Backup code format ITK-XXX", False, f"Invalid format: {backup_code}")
                
            return True, response
        return False, {}

    def test_vouchers_my_endpoint(self):
        """Test GET /api/vouchers/my - should return client's vouchers"""
        print("\n📋 Testing GET /api/vouchers/my...")
        
        success, response = self.run_test(
            "GET /api/vouchers/my",
            "GET",
            "/vouchers/my",
            200
        )
        
        if success:
            vouchers_count = len(response) if isinstance(response, list) else 0
            print(f"   Found {vouchers_count} vouchers")
            
            if vouchers_count > 0:
                voucher = response[0]
                print(f"   First voucher ID: {voucher.get('voucher_id', 'N/A')}")
                print(f"   Backup code: {voucher.get('backup_code', 'N/A')}")
                print(f"   Status: {voucher.get('status', 'N/A')}")
                print(f"   Final price to pay: R$ {voucher.get('final_price_to_pay', 0):.2f}")
                
                # Verify voucher has required fields
                required_fields = ['voucher_id', 'backup_code', 'offer_title', 'status']
                missing_fields = [field for field in required_fields if field not in voucher]
                
                if not missing_fields:
                    self.log_test("Voucher has required fields", True, "All required fields present")
                else:
                    self.log_test("Voucher has required fields", False, f"Missing: {missing_fields}")
                    
                return True, response
            else:
                self.log_test("Vouchers found", False, "No vouchers returned")
                return False, response
        return False, {}

    def test_qr_validate_with_backup_code(self, backup_code):
        """Test POST /api/qr/validate with backup_code - should validate correctly"""
        print(f"\n✅ Testing QR Validation with Backup Code: {backup_code}")
        
        validate_data = {
            "code_hash": backup_code  # API accepts backup_code in code_hash field
        }
        
        success, response = self.run_test(
            "POST /api/qr/validate (backup code)",
            "POST",
            "/qr/validate",
            200,
            data=validate_data
        )
        
        if success:
            print(f"   Success: {response.get('success', False)}")
            print(f"   Message: {response.get('message', 'N/A')}")
            print(f"   Customer: {response.get('customer_name', 'N/A')}")
            print(f"   Credits used: R$ {response.get('credits_used', 0):.2f}")
            print(f"   Amount to pay cash: R$ {response.get('amount_to_pay_cash', 0):.2f}")
            
            # Verify response has required fields
            required_fields = ['success', 'credits_used', 'amount_to_pay_cash']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                self.log_test("Validation response has required fields", True, "All required fields present")
            else:
                self.log_test("Validation response has required fields", False, f"Missing: {missing_fields}")
                
            return True, response
        return False, {}

    def test_sales_history_endpoint(self):
        """Test GET /api/establishments/me/sales-history - should return history and summary"""
        print("\n📊 Testing GET /api/establishments/me/sales-history...")
        
        success, response = self.run_test(
            "GET /api/establishments/me/sales-history",
            "GET",
            "/establishments/me/sales-history",
            200
        )
        
        if success:
            sales = response.get('sales', [])
            summary = response.get('summary', {})
            
            print(f"   Sales count: {len(sales)}")
            print(f"   Total sales: {summary.get('total_sales', 0)}")
            print(f"   Total credits received: R$ {summary.get('total_credits_received', 0):.2f}")
            print(f"   Total cash to receive: R$ {summary.get('total_cash_to_receive', 0):.2f}")
            
            # Verify response structure
            if 'sales' in response and 'summary' in response:
                self.log_test("Sales history has correct structure", True, "Has sales and summary")
                
                # Check if sales have required fields
                if len(sales) > 0:
                    sale = sales[0]
                    required_sale_fields = ['sale_id', 'customer_name', 'offer_title', 'credits_used', 'amount_to_pay_cash']
                    missing_sale_fields = [field for field in required_sale_fields if field not in sale]
                    
                    if not missing_sale_fields:
                        self.log_test("Sale records have required fields", True, "All required fields present")
                    else:
                        self.log_test("Sale records have required fields", False, f"Missing: {missing_sale_fields}")
                
                # Check summary fields
                required_summary_fields = ['total_sales', 'total_credits_received', 'total_cash_to_receive']
                missing_summary_fields = [field for field in required_summary_fields if field not in summary]
                
                if not missing_summary_fields:
                    self.log_test("Summary has required fields", True, "All required fields present")
                else:
                    self.log_test("Summary has required fields", False, f"Missing: {missing_summary_fields}")
                    
                return True, response
            else:
                self.log_test("Sales history has correct structure", False, "Missing sales or summary")
                return False, response
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
        print("🚀 Starting iToke Backend API Tests - Voucher System with Backup Codes")
        print("=" * 80)
        
        # Test 1: Client Login
        print("\n=== CLIENT AUTHENTICATION TESTS ===")
        client_success, client_data = self.test_client_login()
        if not client_success:
            print("❌ Client login failed - cannot continue with tests")
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
        
        print(f"\n=== VOUCHER SYSTEM TESTS (Offer ID: {offer_id}) ===")
        
        # Test 4: QR Generation with backup code format
        qr_success, qr_data = self.test_qr_generation_with_backup_code(offer_id)
        if not qr_success:
            print("❌ QR generation failed - cannot continue with validation tests")
            return False
        
        backup_code = qr_data.get('backup_code')
        
        # Test 5: Get client vouchers
        vouchers_success, vouchers_data = self.test_vouchers_my_endpoint()
        
        # Test 6: Switch to establishment for validation and sales history
        print("\n=== ESTABLISHMENT TESTS ===")
        old_token = self.session_token
        
        if self.test_establishment_login():
            if self.test_get_establishment():
                # Test 7: QR Validation with backup code
                if backup_code:
                    validation_success, validation_data = self.test_qr_validate_with_backup_code(backup_code)
                else:
                    print("⚠️ No backup code available, skipping validation test")
                    validation_success = False
                
                # Test 8: Sales history
                sales_history_success, sales_data = self.test_sales_history_endpoint()
            else:
                print("❌ Could not get establishment data")
                validation_success = False
                sales_history_success = False
        else:
            print("❌ Establishment login failed")
            validation_success = False
            sales_history_success = False
        
        # Restore client token
        self.session_token = old_token
        
        # Summary of critical tests
        critical_tests = [
            ("QR Generation with backup code", qr_success),
            ("Vouchers endpoint", vouchers_success),
            ("QR Validation with backup code", validation_success),
            ("Sales history endpoint", sales_history_success)
        ]
        
        print(f"\n=== CRITICAL FEATURES SUMMARY ===")
        for test_name, success in critical_tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        return all(success for _, success in critical_tests)

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
            print("\n🎉 All critical voucher system features are working correctly!")
            return 0
        else:
            print("\n⚠️  Some critical features failed. Check the voucher system implementation.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())