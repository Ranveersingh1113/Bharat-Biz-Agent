#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Bharat Biz-Agent
Tests all endpoints including health, dashboard, customers, inventory, invoices, udhaar, HITL, and agent processing
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

class BharatBizAgentTester:
    def __init__(self, base_url="https://file-analyzer-91.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()
        self.session.timeout = 30

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
            self.failed_tests.append({"name": name, "details": details})

    def test_api_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                         data: Dict = None, params: Dict = None) -> tuple[bool, Dict]:
        """Generic API test method"""
        url = f"{self.api_base}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, json=data)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
            
            return success, response_data
            
        except Exception as e:
            return False, {"error": str(e)}

    def test_health_check(self):
        """Test health check endpoint"""
        print("\n🔍 Testing Health Check...")
        success, data = self.test_api_endpoint('GET', '/health')
        
        if success:
            required_fields = ['status', 'timestamp', 'database', 'whatsapp', 'sarvam']
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                self.log_test("Health Check - Response Structure", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Health Check - Response Structure", True)
                
            # Check individual components
            self.log_test("Health Check - Database Status", data.get('database') == 'connected')
            self.log_test("Health Check - WhatsApp Config", data.get('whatsapp') == 'configured')
            self.log_test("Health Check - Sarvam Config", data.get('sarvam') == 'configured')
        else:
            self.log_test("Health Check - Endpoint", False, str(data))

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        print("\n📊 Testing Dashboard Stats...")
        success, data = self.test_api_endpoint('GET', '/dashboard/stats')
        
        if success:
            required_fields = ['total_customers', 'total_pending_udhaar', 'today_invoices', 
                             'today_sales', 'low_stock_count', 'pending_approvals']
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                self.log_test("Dashboard Stats - Response Structure", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Dashboard Stats - Response Structure", True)
                
            # Validate data types
            numeric_fields = ['total_customers', 'total_pending_udhaar', 'today_invoices', 
                            'today_sales', 'low_stock_count', 'pending_approvals']
            for field in numeric_fields:
                if field in data:
                    is_numeric = isinstance(data[field], (int, float))
                    self.log_test(f"Dashboard Stats - {field} is numeric", is_numeric)
        else:
            self.log_test("Dashboard Stats - Endpoint", False, str(data))

    def test_customers_api(self):
        """Test customers API endpoints"""
        print("\n👥 Testing Customers API...")
        
        # Test GET customers
        success, data = self.test_api_endpoint('GET', '/customers')
        if success:
            self.log_test("Customers - GET endpoint", True)
            
            if 'customers' in data and isinstance(data['customers'], list):
                self.log_test("Customers - Response structure", True)
                
                if len(data['customers']) > 0:
                    customer = data['customers'][0]
                    required_fields = ['id', 'name', 'phone', 'total_credit', 'credit_limit']
                    missing_fields = [f for f in required_fields if f not in customer]
                    
                    if missing_fields:
                        self.log_test("Customers - Customer structure", False, f"Missing: {missing_fields}")
                    else:
                        self.log_test("Customers - Customer structure", True)
                        
                    # Test individual customer endpoint
                    customer_id = customer['id']
                    success_single, _ = self.test_api_endpoint('GET', f'/customers/{customer_id}')
                    self.log_test("Customers - GET single customer", success_single)
                else:
                    self.log_test("Customers - Has seeded data", False, "No customers found")
            else:
                self.log_test("Customers - Response structure", False, "Invalid response format")
        else:
            self.log_test("Customers - GET endpoint", False, str(data))

    def test_inventory_api(self):
        """Test inventory API endpoints"""
        print("\n📦 Testing Inventory API...")
        
        # Test GET inventory
        success, data = self.test_api_endpoint('GET', '/inventory')
        if success:
            self.log_test("Inventory - GET endpoint", True)
            
            if 'items' in data and isinstance(data['items'], list):
                self.log_test("Inventory - Response structure", True)
                
                if len(data['items']) > 0:
                    item = data['items'][0]
                    required_fields = ['id', 'name', 'fabric_type', 'color', 'width', 
                                     'quantity', 'rate_per_unit', 'gst_rate']
                    missing_fields = [f for f in required_fields if f not in item]
                    
                    if missing_fields:
                        self.log_test("Inventory - Item structure", False, f"Missing: {missing_fields}")
                    else:
                        self.log_test("Inventory - Item structure", True)
                        
                    # Test fabric type filtering
                    fabric_type = item.get('fabric_type')
                    if fabric_type:
                        success_filter, filter_data = self.test_api_endpoint('GET', '/inventory', 
                                                                           params={'fabric_type': fabric_type})
                        self.log_test("Inventory - Fabric type filter", success_filter)
                        
                    # Test color filtering
                    color = item.get('color')
                    if color:
                        success_color, color_data = self.test_api_endpoint('GET', '/inventory', 
                                                                         params={'color': color})
                        self.log_test("Inventory - Color filter", success_color)
                else:
                    self.log_test("Inventory - Has seeded data", False, "No inventory items found")
            else:
                self.log_test("Inventory - Response structure", False, "Invalid response format")
        else:
            self.log_test("Inventory - GET endpoint", False, str(data))
            
        # Test low stock endpoint
        success_low, low_data = self.test_api_endpoint('GET', '/inventory/low-stock')
        self.log_test("Inventory - Low stock endpoint", success_low)

    def test_invoices_api(self):
        """Test invoices API endpoints"""
        print("\n🧾 Testing Invoices API...")
        
        success, data = self.test_api_endpoint('GET', '/invoices')
        if success:
            self.log_test("Invoices - GET endpoint", True)
            
            if 'invoices' in data and isinstance(data['invoices'], list):
                self.log_test("Invoices - Response structure", True)
                
                # Note: Invoices might be empty initially, which is okay
                if len(data['invoices']) > 0:
                    invoice = data['invoices'][0]
                    required_fields = ['id', 'invoice_number', 'customer_name', 'grand_total', 'payment_status']
                    missing_fields = [f for f in required_fields if f not in invoice]
                    
                    if missing_fields:
                        self.log_test("Invoices - Invoice structure", False, f"Missing: {missing_fields}")
                    else:
                        self.log_test("Invoices - Invoice structure", True)
                        
                    # Test individual invoice endpoint
                    invoice_id = invoice['id']
                    success_single, _ = self.test_api_endpoint('GET', f'/invoices/{invoice_id}')
                    self.log_test("Invoices - GET single invoice", success_single)
                else:
                    self.log_test("Invoices - Empty list (expected)", True)
            else:
                self.log_test("Invoices - Response structure", False, "Invalid response format")
        else:
            self.log_test("Invoices - GET endpoint", False, str(data))

    def test_udhaar_api(self):
        """Test udhaar (credit) API endpoints"""
        print("\n💳 Testing Udhaar API...")
        
        # Test udhaar summary
        success_summary, summary_data = self.test_api_endpoint('GET', '/udhaar/summary')
        if success_summary:
            self.log_test("Udhaar - Summary endpoint", True)
            
            required_fields = ['total_pending', 'customer_count']
            missing_fields = [f for f in required_fields if f not in summary_data]
            
            if missing_fields:
                self.log_test("Udhaar - Summary structure", False, f"Missing: {missing_fields}")
            else:
                self.log_test("Udhaar - Summary structure", True)
        else:
            self.log_test("Udhaar - Summary endpoint", False, str(summary_data))
            
        # Test overdue customers
        success_overdue, overdue_data = self.test_api_endpoint('GET', '/udhaar/overdue')
        if success_overdue:
            self.log_test("Udhaar - Overdue endpoint", True)
            
            if 'overdue_customers' in overdue_data:
                self.log_test("Udhaar - Overdue structure", True)
            else:
                self.log_test("Udhaar - Overdue structure", False, "Missing overdue_customers field")
        else:
            self.log_test("Udhaar - Overdue endpoint", False, str(overdue_data))

    def test_hitl_api(self):
        """Test HITL (Human in the Loop) API endpoints"""
        print("\n🔔 Testing HITL API...")
        
        success, data = self.test_api_endpoint('GET', '/hitl/pending')
        if success:
            self.log_test("HITL - Pending requests endpoint", True)
            
            if 'requests' in data and isinstance(data['requests'], list):
                self.log_test("HITL - Response structure", True)
                
                # HITL requests might be empty initially, which is okay
                if len(data['requests']) > 0:
                    request = data['requests'][0]
                    required_fields = ['id', 'request_type', 'customer_name', 'status']
                    missing_fields = [f for f in required_fields if f not in request]
                    
                    if missing_fields:
                        self.log_test("HITL - Request structure", False, f"Missing: {missing_fields}")
                    else:
                        self.log_test("HITL - Request structure", True)
                else:
                    self.log_test("HITL - Empty list (expected)", True)
            else:
                self.log_test("HITL - Response structure", False, "Invalid response format")
        else:
            self.log_test("HITL - Pending requests endpoint", False, str(data))

    def test_agent_processing(self):
        """Test agent text processing with Hinglish"""
        print("\n🤖 Testing Agent Processing...")
        
        test_messages = [
            "Ramesh ko bill bhejo",
            "stock check karo",
            "udhaar batao",
            "payment aaya 5000 ka"
        ]
        
        for message in test_messages:
            success, data = self.test_api_endpoint('POST', '/test/process-text', 
                                                 data={'text': message, 'phone': 'test_user'})
            
            if success:
                if 'response' in data and data['response']:
                    self.log_test(f"Agent - Process '{message}'", True)
                else:
                    self.log_test(f"Agent - Process '{message}'", False, "Empty response")
            else:
                self.log_test(f"Agent - Process '{message}'", False, str(data))
                
        # Test intent classification
        success_intent, intent_data = self.test_api_endpoint('POST', '/test/classify-intent', 
                                                           data={'text': 'Ramesh ko invoice bhejo'})
        self.log_test("Agent - Intent classification", success_intent)

    def test_whatsapp_webhook(self):
        """Test WhatsApp webhook verification"""
        print("\n📱 Testing WhatsApp Webhook...")
        
        # Test webhook verification
        verify_params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'bharat_biz_verify_2026_secure',
            'hub.challenge': 'test_challenge_123'
        }
        
        try:
            response = self.session.get(f"{self.api_base}/webhook", params=verify_params, timeout=10)
            
            if response.status_code == 200 and response.text == 'test_challenge_123':
                self.log_test("WhatsApp - Webhook verification", True)
            else:
                self.log_test("WhatsApp - Webhook verification", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("WhatsApp - Webhook verification", False, str(e))

    def test_conversations_api(self):
        """Test conversations API"""
        print("\n💬 Testing Conversations API...")
        
        success, data = self.test_api_endpoint('GET', '/conversations')
        if success:
            self.log_test("Conversations - GET endpoint", True)
            
            if 'conversations' in data:
                self.log_test("Conversations - Response structure", True)
            else:
                self.log_test("Conversations - Response structure", False, "Missing conversations field")
        else:
            self.log_test("Conversations - GET endpoint", False, str(data))

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Bharat Biz-Agent Backend API Tests...")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run all test suites
        self.test_health_check()
        self.test_dashboard_stats()
        self.test_customers_api()
        self.test_inventory_api()
        self.test_invoices_api()
        self.test_udhaar_api()
        self.test_hitl_api()
        self.test_agent_processing()
        self.test_whatsapp_webhook()
        self.test_conversations_api()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                print(f"  • {test['name']}: {test['details']}")
        else:
            print("\n🎉 All tests passed!")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n✨ Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = BharatBizAgentTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n💥 Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())