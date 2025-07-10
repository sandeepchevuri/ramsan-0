import requests
import unittest
import uuid
import json
import os
import base64
from io import BytesIO
from PIL import Image

class JoatxAPITester:
    def __init__(self, base_url="https://81d14a74-3406-418a-8498-2457090785ea.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.analysis_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        if not files:
            headers['Content-Type'] = 'application/json'
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except json.JSONDecodeError:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                except:
                    pass
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test the health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "/api/health",
            200
        )
        if success:
            print(f"Health check response: {response}")
        return success

    def test_analyze_image(self):
        """Test image analysis endpoint"""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        files = {
            'file': ('test_image.jpg', img_byte_arr, 'image/jpeg')
        }
        
        success, response = self.run_test(
            "Analyze Image",
            "POST",
            "/api/analyze-image",
            200,
            files=files
        )
        
        if success:
            print(f"Analysis ID: {response.get('analysis_id')}")
            print(f"Problem identified: {response.get('analysis', {}).get('problem_identified')}")
            print(f"Difficulty level: {response.get('analysis', {}).get('difficulty_level')}")
            print(f"Can DIY: {response.get('analysis', {}).get('can_diy')}")
            
            # Store analysis ID for later tests
            self.analysis_id = response.get('analysis_id')
            
            # Store problem type for nearby services test
            self.problem_type = response.get('analysis', {}).get('professional_type')
        
        return success

    def test_get_analysis_by_id(self):
        """Test getting analysis by ID"""
        if not self.analysis_id:
            print("❌ No analysis ID available, skipping test")
            return False
            
        success, response = self.run_test(
            "Get Analysis by ID",
            "GET",
            f"/api/analysis/{self.analysis_id}",
            200
        )
        
        if success:
            print(f"Retrieved analysis with ID: {response.get('id')}")
        
        return success

    def test_find_nearby_services(self):
        """Test finding nearby services"""
        if not hasattr(self, 'problem_type'):
            print("❌ No problem type available, using default")
            self.problem_type = "electrician"
            
        # Mock location data (New York City coordinates)
        data = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "problem_type": self.problem_type
        }
        
        success, response = self.run_test(
            "Find Nearby Services",
            "POST",
            "/api/find-nearby",
            200,
            data=data
        )
        
        if success:
            print(f"Found {response.get('total_found')} nearby services")
            if response.get('services'):
                print(f"First service: {response.get('services')[0].get('name')}")
        
        return success

    def test_emergency_contact(self):
        """Test emergency contact endpoint"""
        data = {
            "problem_type": "electrical",
            "urgency": "high",
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "123 Test St, New York, NY"
            }
        }
        
        success, response = self.run_test(
            "Emergency Contact",
            "POST",
            "/api/emergency-contact",
            200,
            data=data
        )
        
        if success:
            print(f"Emergency request ID: {response.get('request_id')}")
            print(f"Response message: {response.get('message')}")
        
        return success

    def test_get_all_guides(self):
        """Test getting all guides (backward compatibility)"""
        success, response = self.run_test(
            "Get All Guides (Legacy)",
            "GET",
            "/api/guides",
            200
        )
        
        if success and isinstance(response, list):
            print(f"Found {len(response)} guides in legacy endpoint")
        
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Joatx AI Repair Assistant API Tests")
        
        # Run tests
        self.test_health_endpoint()
        self.test_analyze_image()
        self.test_get_analysis_by_id()
        self.test_find_nearby_services()
        self.test_emergency_contact()
        self.test_get_all_guides()  # Legacy endpoint test
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = JoatxAPITester()
    tester.run_all_tests()