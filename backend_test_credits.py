#!/usr/bin/env python3
"""
Backend API Testing for iToke Platform - Credits Reserved Test
Testing QR generation with credits to verify credits_reserved field
"""

import requests
import sys
import json
from datetime import datetime

class iTokeCreditsTester:
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

    def create_user_with_credits(self):
        """Create a user with credits through referral system"""
        print(f"\n💰 Creating user with credits through referral system...")
        
        # Create referrer who will buy tokens (and get commission)
        referrer_email = f"referrer_credits_{datetime.now().strftime('%H%M%S')}@teste.com"
        buyer_email = f"buyer_credits_{datetime.now().strftime('%H%M%S')}@teste.com"
        
        # 1. Create referrer
        referrer_success, referrer_data = self.login_as_client(referrer_email)
        if not referrer_success:
            return False, None
        
        referrer_code = referrer_data.get('referral_code')
        print(f"   Created referrer with code: {referrer_code}")
        
        # 2. Create buyer and apply referral
        buyer_success, buyer_data = self.login_as_client(buyer_email)
        if not buyer_success:
            return False, None
        
        # Apply referral code
        apply_success, _ = self.run_test(
            "Apply referral code to buyer",
            "POST",
            "/auth/apply-referral",
            200,
            data={"referral_code": referrer_code}
        )
        
        if not apply_success:
            return False, None
        
        # 3. Buyer purchases tokens (this will give commission to referrer)
        purchase_data = {"packages": 2}  # Buy 2 packages to give R$2 commission
        
        success, response = self.run_test(
            "Buyer purchases tokens",
            "POST",
            "/tokens/purchase",
            200,
            data=purchase_data
        )
        
        if not success:
            return False, None
        
        # 4. Switch back to referrer to check credits
        referrer_success, referrer_data = self.login_as_client(referrer_email)
        if referrer_success:
            _, tokens, credits = self.get_user_balance()
            if credits > 0:
                print(f"   Referrer now has R$ {credits:.2f} credits!")
                return True, referrer_email
        
        return False, None

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

    def test_qr_generation_with_specific_credits(self, offer_id, use_credits_amount):
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
            print(f"   Response keys: {list(response.keys())}")
            
            # Verify credits_reserved is in response
            if 'credits_reserved' in response:
                self.log_test("QR response includes credits_reserved field", True, f"credits_reserved: {credits_reserved}")
                
                # Verify the amount is correct (should be min of requested amount and available credits)
                if credits_reserved == use_credits_amount:
                    self.log_test("Credits reserved amount matches request", True, f"Expected: {use_credits_amount}, Got: {credits_reserved}")
                else:
                    self.log_test("Credits reserved amount matches request", False, f"Expected: {use_credits_amount}, Got: {credits_reserved}")
            else:
                self.log_test("QR response includes credits_reserved field", False, "credits_reserved field missing from response")
            
            return True, response
        return False, {}

    def run_credits_test(self):
        """Run credits-specific tests"""
        print("🚀 Starting iToke Credits Reserved Tests")
        print("=" * 60)
        
        # 1. Create user with credits
        print("\n=== SETUP: CREATE USER WITH CREDITS ===")
        credits_success, user_with_credits_email = self.create_user_with_credits()
        if not credits_success:
            print("❌ Could not create user with credits - cannot test credits_reserved")
            return False
        
        # 2. Login as user with credits
        print(f"\n=== LOGIN AS USER WITH CREDITS ===")
        login_success, user_data = self.login_as_client(user_with_credits_email)
        if not login_success:
            return False
        
        # 3. Get current balance
        balance_success, tokens, credits = self.get_user_balance()
        if not balance_success or credits <= 0:
            print(f"❌ User has no credits (R$ {credits:.2f}) - cannot test")
            return False
        
        # 4. Get test offer
        offer_id, offer_price = self.get_test_offer_id()
        if not offer_id:
            print("❌ No test offer available")
            return False
        
        # 5. Test QR generation with different credit amounts
        print(f"\n=== QR GENERATION WITH CREDITS (Available: R$ {credits:.2f}) ===")
        
        # Test with 5.50 if user has enough
        if credits >= 5.50:
            self.test_qr_generation_with_specific_credits(offer_id, 5.50)
        else:
            print(f"⚠️ User has only R$ {credits:.2f}, testing with available amount")
            self.test_qr_generation_with_specific_credits(offer_id, credits)
        
        # Test with 0 credits
        self.test_qr_generation_with_specific_credits(offer_id, 0)
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 CREDITS TEST SUMMARY")
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
    tester = iTokeCreditsTester()
    
    try:
        success = tester.run_credits_test()
        all_passed = tester.print_summary()
        
        if all_passed:
            print("\n🎉 All credits tests passed!")
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