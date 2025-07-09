import requests
import unittest
import uuid
import json

class JoatxAPITester:
    def __init__(self, base_url="https://81d14a74-3406-418a-8498-2457090785ea.preview.emergentagent.com"):
        self.base_url = base_url
        self.user_id = f"test_user_{uuid.uuid4()}"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
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

    def test_get_all_guides(self):
        """Test getting all guides"""
        success, response = self.run_test(
            "Get All Guides",
            "GET",
            "/api/guides",
            200
        )
        if success and isinstance(response, list):
            print(f"Found {len(response)} guides")
            if len(response) > 0:
                self.guide_id = response[0]['id']
                print(f"Using guide ID: {self.guide_id}")
        return success

    def test_get_guide_by_id(self):
        """Test getting a specific guide by ID"""
        if not hasattr(self, 'guide_id'):
            print("❌ No guide ID available, skipping test")
            return False
            
        success, response = self.run_test(
            "Get Guide by ID",
            "GET",
            f"/api/guides/{self.guide_id}",
            200
        )
        if success:
            print(f"Guide title: {response.get('title')}")
        return success

    def test_get_categories(self):
        """Test getting all categories"""
        success, response = self.run_test(
            "Get Categories",
            "GET",
            "/api/categories",
            200
        )
        if success and isinstance(response, list):
            print(f"Found categories: {response}")
            if len(response) > 0:
                self.category = response[0]
        return success

    def test_get_guides_by_category(self):
        """Test getting guides by category"""
        if not hasattr(self, 'category'):
            print("❌ No category available, skipping test")
            return False
            
        success, response = self.run_test(
            "Get Guides by Category",
            "GET",
            f"/api/guides/category/{self.category}",
            200
        )
        if success and isinstance(response, list):
            print(f"Found {len(response)} guides in category '{self.category}'")
        return success

    def test_update_progress(self):
        """Test updating user progress"""
        if not hasattr(self, 'guide_id'):
            print("❌ No guide ID available, skipping test")
            return False
            
        data = {
            "user_id": self.user_id,
            "guide_id": self.guide_id,
            "current_step": 2,
            "completed": False
        }
        
        success, response = self.run_test(
            "Update Progress",
            "POST",
            "/api/progress",
            200,
            data=data
        )
        return success

    def test_get_progress(self):
        """Test getting user progress"""
        if not hasattr(self, 'guide_id'):
            print("❌ No guide ID available, skipping test")
            return False
            
        success, response = self.run_test(
            "Get Progress",
            "GET",
            f"/api/progress/{self.user_id}/{self.guide_id}",
            200
        )
        if success:
            print(f"User progress: {response}")
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Joatx API Tests")
        
        # Run tests
        self.test_health_endpoint()
        self.test_get_all_guides()
        self.test_get_guide_by_id()
        self.test_get_categories()
        self.test_get_guides_by_category()
        self.test_update_progress()
        self.test_get_progress()
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = JoatxAPITester()
    tester.run_all_tests()