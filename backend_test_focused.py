#!/usr/bin/env python3
"""
Backend API Testing for iToke Platform - Focused Tests for Specific Issues
Testing the specific issues reported:
1. POST /api/qr/generate com use_credits=5.50 - deve retornar credits_reserved no response
2. POST /api/qr/generate sem créditos - credits_reserved deve ser 0
3. POST /api/tokens/purchase - NÃO deve dar créditos ao próprio comprador
4. Verificar que distribute_commissions só dá créditos para referrers, não para purchaser
"""

import requests
import sys
import json
from datetime import datetime

class iTokeFocusedTester:
    def __init__(self, base_url="https://draft-offer-mode.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.user_id = None
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

    def login_as_client(self, email="cliente@teste.com"):
        """Login as client user"""
        print(f"\n🔐 Logging in as client: {email}")
        
        login_data = {
            "email": email,
            "name": "Cliente Teste",
            "role": "client"
        }
        
        success, response = self.run_test(
            f"Login as client ({email})",
            "POST",
            "/auth/email-login",
            200,
            data=login_data
        )
        
        if success and 'session_token' in response:
            self.session_token = response['session_token']
            user_data = response.get('user', {})
            self.user_id = user_data.get('user_id')
            print(f"   Session token: {self.session_token[:20]}...")
            print(f"   User ID: {self.user_id}")
            print(f"   Tokens: {user_data.get('tokens', 0)}")
            print(f"   Credits: {user_data.get('credits', 0)}")
            return True, user_data
        return False, {}

    def get_user_balance(self):
        """Get current user balance"""
        success, response = self.run_test(
            "Get user balance",
            "GET",
            "/auth/me",
            200
        )
        
        if success:
            tokens = response.get('tokens', 0)
            credits = response.get('credits', 0)
            print(f"   Current balance - Tokens: {tokens}, Credits: R$ {credits:.2f}")
            return True, tokens, credits
        return False, 0, 0

    def add_credits_to_user(self, amount=10.0):
        """Add credits to user for testing (simulating commission earnings)"""
        print(f"\n💰 Adding R$ {amount:.2f} credits to user for testing...")
        
        # We'll simulate this by creating a referral transaction
        # First, let's check if we can add credits directly via the database
        # Since we can't access the database directly, we'll use the referral system
        
        # Create a referrer user first
        referrer_email = f"referrer_{datetime.now().strftime('%H%M%S')}@teste.com"
        referrer_success, referrer_data = self.login_as_client(referrer_email)
        
        if referrer_success:
            referrer_code = referrer_data.get('referral_code')
            print(f"   Created referrer with code: {referrer_code}")
            
            # Now login as our main user and apply referral
            main_success, main_data = self.login_as_client("cliente@teste.com")
            if main_success:
                # Apply referral code
                apply_success, _ = self.run_test(
                    "Apply referral code",
                    "POST",
                    "/auth/apply-referral",
                    200,
                    data={"referral_code": referrer_code}
                )
                
                if apply_success:
                    print(f"   Applied referral code successfully")
                    return True
        
        return False

    def get_test_offer_id(self):
        """Get an existing offer ID for testing"""
        print("\n🔍 Getting test offer ID...")
        
        success, response = self.run_test(
            "GET /api/offers",
            "GET",
            "/offers?limit=1",
            200
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            offer_id = response[0].get('offer_id')
            offer_price = response[0].get('discounted_price', 0)
            print(f"   Using offer ID: {offer_id}")
            print(f"   Offer price: R$ {offer_price:.2f}")
            return offer_id, offer_price
        
        print("   No offers found")
        return None, 0

    def test_qr_generation_with_credits(self, offer_id, use_credits_amount):
        """Test QR generation with specific credit amount"""
        print(f"\n🎫 Testing QR generation with R$ {use_credits_amount:.2f} credits...")
        
        qr_data = {
            "offer_id": offer_id,
            "use_credits": use_credits_amount
        }
        
        success, response = self.run_test(
            f"QR generation with R$ {use_credits_amount:.2f} credits",
            "POST",
            "/qr/generate",
            200,
            data=qr_data
        )
        
        if success:
            credits_reserved = response.get('credits_reserved', 0)
            print(f"   QR ID: {response.get('qr_id', 'N/A')}")
            print(f"   Credits reserved: R$ {credits_reserved:.2f}")
            
            # Verify credits_reserved is in response
            if 'credits_reserved' in response:
                self.log_test("QR response includes credits_reserved", True, f"credits_reserved: {credits_reserved}")
                
                # Verify the amount is correct
                if credits_reserved == use_credits_amount:
                    self.log_test("Credits reserved amount correct", True, f"Expected: {use_credits_amount}, Got: {credits_reserved}")
                else:
                    self.log_test("Credits reserved amount correct", False, f"Expected: {use_credits_amount}, Got: {credits_reserved}")
            else:
                self.log_test("QR response includes credits_reserved", False, "credits_reserved field missing from response")
            
            return True, response
        return False, {}

    def test_qr_generation_without_credits(self, offer_id):
        """Test QR generation without using credits"""
        print(f"\n🎫 Testing QR generation without credits...")
        
        qr_data = {
            "offer_id": offer_id,
            "use_credits": 0
        }
        
        success, response = self.run_test(
            "QR generation without credits",
            "POST",
            "/qr/generate",
            200,
            data=qr_data
        )
        
        if success:
            credits_reserved = response.get('credits_reserved', 0)
            print(f"   QR ID: {response.get('qr_id', 'N/A')}")
            print(f"   Credits reserved: R$ {credits_reserved:.2f}")
            
            # Verify credits_reserved is 0
            if credits_reserved == 0:
                self.log_test("Credits reserved is 0 when not using credits", True, f"credits_reserved: {credits_reserved}")
            else:
                self.log_test("Credits reserved is 0 when not using credits", False, f"Expected: 0, Got: {credits_reserved}")
            
            return True, response
        return False, {}

    def test_token_purchase_no_self_commission(self):
        """Test that token purchase doesn't give commission to the purchaser themselves"""
        print(f"\n💳 Testing token purchase - no self-commission...")
        
        # Get initial balance
        balance_success, initial_tokens, initial_credits = self.get_user_balance()
        if not balance_success:
            return False
        
        print(f"   Initial balance - Tokens: {initial_tokens}, Credits: R$ {initial_credits:.2f}")
        
        # Purchase 1 package (7 tokens)
        purchase_data = {
            "packages": 1
        }
        
        success, response = self.run_test(
            "Purchase token package",
            "POST",
            "/tokens/purchase",
            200,
            data=purchase_data
        )
        
        if success:
            print(f"   Purchase ID: {response.get('purchase_id', 'N/A')}")
            print(f"   New token balance: {response.get('new_balance', 'N/A')}")
            
            # Check balance after purchase
            balance_success, final_tokens, final_credits = self.get_user_balance()
            if balance_success:
                tokens_gained = final_tokens - initial_tokens
                credits_gained = final_credits - initial_credits
                
                print(f"   Final balance - Tokens: {final_tokens}, Credits: R$ {final_credits:.2f}")
                print(f"   Tokens gained: {tokens_gained}")
                print(f"   Credits gained: R$ {credits_gained:.2f}")
                
                # Verify tokens were added (should be 7)
                if tokens_gained == 7:
                    self.log_test("Tokens correctly added to purchaser", True, f"Gained {tokens_gained} tokens")
                else:
                    self.log_test("Tokens correctly added to purchaser", False, f"Expected 7 tokens, got {tokens_gained}")
                
                # Verify NO credits were added to purchaser (should be 0)
                if credits_gained == 0:
                    self.log_test("No commission given to purchaser", True, f"Credits gained: {credits_gained}")
                else:
                    self.log_test("No commission given to purchaser", False, f"Purchaser incorrectly received R$ {credits_gained:.2f} commission")
                
                return True
        
        return False

    def test_distribute_commissions_logic(self):
        """Test that distribute_commissions only gives to referrers, not purchaser"""
        print(f"\n🔗 Testing commission distribution logic...")
        
        # Create a referral chain: Referrer -> Purchaser
        referrer_email = f"referrer_test_{datetime.now().strftime('%H%M%S')}@teste.com"
        purchaser_email = f"purchaser_test_{datetime.now().strftime('%H%M%S')}@teste.com"
        
        # 1. Create referrer
        referrer_success, referrer_data = self.login_as_client(referrer_email)
        if not referrer_success:
            return False
        
        referrer_code = referrer_data.get('referral_code')
        referrer_id = referrer_data.get('user_id')
        print(f"   Created referrer: {referrer_id} with code: {referrer_code}")
        
        # Get referrer's initial balance
        _, referrer_initial_tokens, referrer_initial_credits = self.get_user_balance()
        
        # 2. Create purchaser and apply referral
        purchaser_success, purchaser_data = self.login_as_client(purchaser_email)
        if not purchaser_success:
            return False
        
        purchaser_id = purchaser_data.get('user_id')
        print(f"   Created purchaser: {purchaser_id}")
        
        # Apply referral code
        apply_success, _ = self.run_test(
            "Apply referral code to purchaser",
            "POST",
            "/auth/apply-referral",
            200,
            data={"referral_code": referrer_code}
        )
        
        if not apply_success:
            return False
        
        # Get purchaser's initial balance
        _, purchaser_initial_tokens, purchaser_initial_credits = self.get_user_balance()
        
        # 3. Purchaser buys tokens
        purchase_data = {"packages": 1}
        
        success, response = self.run_test(
            "Purchaser buys tokens",
            "POST",
            "/tokens/purchase",
            200,
            data=purchase_data
        )
        
        if not success:
            return False
        
        # 4. Check final balances
        # Check purchaser balance
        _, purchaser_final_tokens, purchaser_final_credits = self.get_user_balance()
        
        # Check referrer balance
        self.login_as_client(referrer_email)
        _, referrer_final_tokens, referrer_final_credits = self.get_user_balance()
        
        # Analysis
        purchaser_tokens_gained = purchaser_final_tokens - purchaser_initial_tokens
        purchaser_credits_gained = purchaser_final_credits - purchaser_initial_credits
        referrer_credits_gained = referrer_final_credits - referrer_initial_credits
        
        print(f"   Purchaser tokens gained: {purchaser_tokens_gained}")
        print(f"   Purchaser credits gained: R$ {purchaser_credits_gained:.2f}")
        print(f"   Referrer credits gained: R$ {referrer_credits_gained:.2f}")
        
        # Verify purchaser got tokens but NO commission
        if purchaser_tokens_gained == 7:
            self.log_test("Purchaser received tokens", True, f"Got {purchaser_tokens_gained} tokens")
        else:
            self.log_test("Purchaser received tokens", False, f"Expected 7, got {purchaser_tokens_gained}")
        
        if purchaser_credits_gained == 0:
            self.log_test("Purchaser did NOT receive commission", True, "No self-commission")
        else:
            self.log_test("Purchaser did NOT receive commission", False, f"Incorrectly received R$ {purchaser_credits_gained:.2f}")
        
        # Verify referrer got commission
        if referrer_credits_gained > 0:
            self.log_test("Referrer received commission", True, f"Got R$ {referrer_credits_gained:.2f}")
        else:
            self.log_test("Referrer received commission", False, "No commission received")
        
        return True

    def run_focused_tests(self):
        """Run all focused tests"""
        print("🚀 Starting iToke Focused Backend Tests")
        print("=" * 60)
        
        # 1. Login as client
        print("\n=== AUTHENTICATION ===")
        client_success, client_data = self.login_as_client()
        if not client_success:
            print("❌ Client login failed - cannot continue")
            return False
        
        # 2. Get test offer
        offer_id, offer_price = self.get_test_offer_id()
        if not offer_id:
            print("❌ No test offer available - cannot test QR generation")
            return False
        
        # 3. Test QR generation without credits
        print("\n=== QR GENERATION TESTS ===")
        self.test_qr_generation_without_credits(offer_id)
        
        # 4. Test QR generation with credits (if user has credits)
        _, tokens, credits = self.get_user_balance()
        if credits >= 5.50:
            self.test_qr_generation_with_credits(offer_id, 5.50)
        else:
            print(f"⚠️ User has only R$ {credits:.2f} credits, cannot test with R$ 5.50")
            if credits > 0:
                self.test_qr_generation_with_credits(offer_id, credits)
        
        # 5. Test token purchase (no self-commission)
        print("\n=== TOKEN PURCHASE TESTS ===")
        if tokens >= 1:  # Need at least 1 token to test purchase
            self.test_token_purchase_no_self_commission()
        else:
            print("⚠️ User has no tokens, skipping token purchase test")
        
        # 6. Test commission distribution logic
        print("\n=== COMMISSION DISTRIBUTION TESTS ===")
        self.test_distribute_commissions_logic()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST SUMMARY")
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
    tester = iTokeFocusedTester()
    
    try:
        success = tester.run_focused_tests()
        all_passed = tester.print_summary()
        
        if all_passed:
            print("\n🎉 All focused tests passed!")
            return 0
        else:
            print("\n⚠️ Some tests failed.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())