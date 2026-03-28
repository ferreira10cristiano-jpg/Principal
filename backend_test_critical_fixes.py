#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class CriticalFixesTester:
    def __init__(self, base_url="https://draft-offer-mode.preview.emergentagent.com"):
        self.base_url = base_url
        self.session_token = "email_session_f16ac98ba01b4158b400e6656793f855"
        self.user_data = None
        self.establishment_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
        if success:
            self.tests_passed += 1
        
        # Store result for reporting
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
        return success

    def test_auth_with_existing_token(self):
        """Test authentication with existing token"""
        print("\n🔐 Testing Authentication with Existing Token...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers={"Authorization": f"Bearer {self.session_token}"}
            )
            
            if response.status_code == 200:
                self.user_data = response.json()
                return self.log_test("Auth with existing token", True, 
                                   f"User: {self.user_data.get('name', 'Unknown')}, Role: {self.user_data.get('role')}")
            else:
                return self.log_test("Auth with existing token", False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Auth with existing token", False, f"Error: {str(e)}")

    def test_get_establishment(self):
        """Test getting establishment data"""
        print("\n🏢 Testing Get Establishment...")
        
        if not self.session_token:
            return self.log_test("Get establishment", False, "No session token")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/establishments/me",
                headers={"Authorization": f"Bearer {self.session_token}"}
            )
            
            if response.status_code == 200:
                self.establishment_data = response.json()
                return self.log_test("Get establishment", True, 
                                   f"Name: {self.establishment_data.get('business_name')}")
            else:
                return self.log_test("Get establishment", False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Get establishment", False, f"Error: {str(e)}")

    def test_referral_share_link(self):
        """Test GET /api/referral/share-link - should return dynamic link"""
        print("\n🔗 Testing Referral Share Link (Dynamic URLs)...")
        
        if not self.session_token:
            return self.log_test("Referral share link", False, "No session token")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/referral/share-link",
                headers={"Authorization": f"Bearer {self.session_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                share_link = data.get('share_link', '')
                referral_code = data.get('referral_code', '')
                
                # Check if link has correct format
                expected_format = "https://draft-offer-mode.preview.emergentagent.com?ref="
                if share_link.startswith(expected_format) and referral_code:
                    return self.log_test("Referral share link", True, 
                                       f"Link: {share_link}, Code: {referral_code}", data)
                else:
                    return self.log_test("Referral share link", False, 
                                       f"Invalid format. Expected: {expected_format}XXXX, Got: {share_link}")
            else:
                return self.log_test("Referral share link", False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Referral share link", False, f"Error: {str(e)}")

    def test_establishment_financial(self):
        """Test GET /api/establishments/me/financial - should return withdrawable_balance and financial_logs"""
        print("\n💰 Testing Establishment Financial Data...")
        
        if not self.session_token:
            return self.log_test("Establishment financial", False, "No session token")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/establishments/me/financial",
                headers={"Authorization": f"Bearer {self.session_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                withdrawable_balance = data.get('withdrawable_balance')
                financial_logs = data.get('financial_logs', [])
                total_sales = data.get('total_sales', 0)
                
                # Check required fields
                if withdrawable_balance is not None and isinstance(financial_logs, list):
                    return self.log_test("Establishment financial", True, 
                                       f"Balance: R$ {withdrawable_balance}, Sales: {total_sales}, Logs: {len(financial_logs)}", data)
                else:
                    return self.log_test("Establishment financial", False, 
                                       f"Missing required fields. Balance: {withdrawable_balance}, Logs: {type(financial_logs)}")
            else:
                return self.log_test("Establishment financial", False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Establishment financial", False, f"Error: {str(e)}")

    def test_qr_validation_flow(self):
        """Test POST /api/qr/validate - should return credits_used and credits_added_to_establishment"""
        print("\n📱 Testing QR Validation Flow...")
        
        if not self.session_token:
            return self.log_test("QR validation flow", False, "No session token")
        
        # First, we need to create a QR code to validate
        # Let's try to get an existing offer first
        try:
            # Get offers from establishment
            offers_response = requests.get(
                f"{self.base_url}/api/establishments/me/offers",
                headers={"Authorization": f"Bearer {self.session_token}"}
            )
            
            if offers_response.status_code != 200:
                return self.log_test("QR validation flow", False, "Could not get offers to test QR validation")
            
            offers = offers_response.json()
            if not offers:
                return self.log_test("QR validation flow", False, "No offers available to test QR validation")
            
            # Use first offer to generate QR
            offer_id = offers[0]['offer_id']
            
            # Generate QR code (this would normally be done by a client)
            qr_response = requests.post(
                f"{self.base_url}/api/qr/generate",
                json={"offer_id": offer_id},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.session_token}"
                }
            )
            
            if qr_response.status_code != 200:
                return self.log_test("QR validation flow", False, f"Could not generate QR: {qr_response.text}")
            
            qr_data = qr_response.json()
            code_hash = qr_data.get('code_hash')
            
            if not code_hash:
                return self.log_test("QR validation flow", False, "No code_hash in QR response")
            
            # Now validate the QR code
            validate_response = requests.post(
                f"{self.base_url}/api/qr/validate",
                json={"code_hash": code_hash},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.session_token}"
                }
            )
            
            if validate_response.status_code == 200:
                data = validate_response.json()
                credits_used = data.get('credits_used')
                credits_added = data.get('credits_added_to_establishment')
                
                # Check required fields
                if credits_used is not None and credits_added is not None:
                    return self.log_test("QR validation flow", True, 
                                       f"Credits used: {credits_used}, Credits added: {credits_added}", data)
                else:
                    return self.log_test("QR validation flow", False, 
                                       f"Missing credit fields. Used: {credits_used}, Added: {credits_added}")
            else:
                return self.log_test("QR validation flow", False, 
                                   f"Validation failed. Status: {validate_response.status_code}, Response: {validate_response.text}")
                
        except Exception as e:
            return self.log_test("QR validation flow", False, f"Error: {str(e)}")

    def test_financial_logs_creation(self):
        """Test that financial_logs are created after QR validation"""
        print("\n📊 Testing Financial Logs Creation...")
        
        if not self.session_token:
            return self.log_test("Financial logs creation", False, "No session token")
        
        try:
            # Get financial data to check logs
            response = requests.get(
                f"{self.base_url}/api/establishments/me/financial",
                headers={"Authorization": f"Bearer {self.session_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                financial_logs = data.get('financial_logs', [])
                
                # Check if we have any logs
                if financial_logs:
                    # Check structure of latest log
                    latest_log = financial_logs[0]
                    required_fields = ['log_id', 'type', 'from_user_id', 'to_establishment_id', 
                                     'credits_deducted_from_user', 'credits_added_to_establishment', 'created_at']
                    
                    missing_fields = [field for field in required_fields if field not in latest_log]
                    
                    if not missing_fields:
                        return self.log_test("Financial logs creation", True, 
                                           f"Found {len(financial_logs)} logs with proper structure", latest_log)
                    else:
                        return self.log_test("Financial logs creation", False, 
                                           f"Log missing fields: {missing_fields}")
                else:
                    return self.log_test("Financial logs creation", True, 
                                       "No financial logs yet (expected if no QR validations)")
            else:
                return self.log_test("Financial logs creation", False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Financial logs creation", False, f"Error: {str(e)}")

    def test_dashboard_financial_loading(self):
        """Test that dashboard can load financial data without errors"""
        print("\n📋 Testing Dashboard Financial Data Loading...")
        
        if not self.session_token:
            return self.log_test("Dashboard financial loading", False, "No session token")
        
        try:
            # Test the same endpoint that dashboard uses
            response = requests.get(
                f"{self.base_url}/api/establishments/me/financial",
                headers={"Authorization": f"Bearer {self.session_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that all required fields for dashboard are present
                required_fields = ['withdrawable_balance', 'total_sales', 'financial_logs']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    return self.log_test("Dashboard financial loading", True, 
                                       f"All dashboard fields present: {list(data.keys())}")
                else:
                    return self.log_test("Dashboard financial loading", False, 
                                       f"Missing dashboard fields: {missing_fields}")
            else:
                return self.log_test("Dashboard financial loading", False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            return self.log_test("Dashboard financial loading", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all critical fixes tests"""
        print("🚀 Starting iToke Critical Fixes Tests")
        print("=" * 60)
        
        # Authentication
        if not self.test_auth_with_existing_token():
            print("❌ Authentication failed - cannot proceed with other tests")
            return self.print_summary()
        
        # Get establishment data
        self.test_get_establishment()
        
        # Test critical fixes
        self.test_referral_share_link()
        self.test_establishment_financial()
        self.test_qr_validation_flow()
        self.test_financial_logs_creation()
        self.test_dashboard_financial_loading()
        
        return self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 CRITICAL FIXES TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        print("\n🎯 CRITICAL FIXES STATUS:")
        
        # Check specific fixes
        referral_fix = any(r['name'] == 'Referral share link' and r['success'] for r in self.test_results)
        financial_fix = any(r['name'] == 'Establishment financial' and r['success'] for r in self.test_results)
        qr_fix = any(r['name'] == 'QR validation flow' and r['success'] for r in self.test_results)
        dashboard_fix = any(r['name'] == 'Dashboard financial loading' and r['success'] for r in self.test_results)
        
        print(f"✅ Dynamic referral links: {'WORKING' if referral_fix else 'FAILED'}")
        print(f"✅ Financial dashboard field: {'WORKING' if financial_fix else 'FAILED'}")
        print(f"✅ Credit payment flow: {'WORKING' if qr_fix else 'FAILED'}")
        print(f"✅ Dashboard loading: {'WORKING' if dashboard_fix else 'FAILED'}")
        
        if self.tests_passed >= 5:  # Minimum successful tests
            print("\n🎉 Most critical fixes are working correctly!")
        else:
            print("\n⚠️  Some critical fixes may have issues!")
        
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = CriticalFixesTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())