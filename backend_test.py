#!/usr/bin/env python3
"""
Backend API Testing Script for Project Management App
Tests authentication, project management, and task management endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://a026955e-0867-42b9-96d1-261e6adb907b.preview.emergentagent.com/api"

class ProjectManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.project_id = None
        self.task_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
    def test_user_registration(self):
        """Test user registration endpoint"""
        print("\n=== Testing User Registration ===")
        
        # Test data with realistic information
        user_data = {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@projectmanager.com",
            "password": "SecurePass123!",
            "role": "Manager"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.user_data = data["user"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Registration", True, f"User {data['user']['name']} registered successfully")
                    return True
                else:
                    self.log_test("User Registration", False, "Missing access_token or user in response")
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            
        return False
        
    def test_user_login(self):
        """Test user login endpoint"""
        print("\n=== Testing User Login ===")
        
        login_data = {
            "email": "sarah.johnson@projectmanager.com",
            "password": "SecurePass123!"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    # Update token in case it's different
                    self.auth_token = data["access_token"]
                    self.user_data = data["user"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Login", True, f"User {data['user']['name']} logged in successfully")
                    return True
                else:
                    self.log_test("User Login", False, "Missing access_token or user in response")
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            
        return False
        
    def test_get_user_profile(self):
        """Test authenticated user profile endpoint"""
        print("\n=== Testing User Profile ===")
        
        if not self.auth_token:
            self.log_test("User Profile", False, "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if "email" in data and "name" in data:
                    self.log_test("User Profile", True, f"Retrieved profile for {data['name']}")
                    return True
                else:
                    self.log_test("User Profile", False, "Missing user data in response")
            else:
                self.log_test("User Profile", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Profile", False, f"Exception: {str(e)}")
            
        return False
        
    def test_create_project(self):
        """Test project creation endpoint"""
        print("\n=== Testing Project Creation ===")
        
        if not self.auth_token:
            self.log_test("Project Creation", False, "No auth token available")
            return False
            
        project_data = {
            "title": "Mobile App Development",
            "description": "Development of a cross-platform mobile application for customer engagement"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/projects", json=project_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "title" in data:
                    self.project_id = data["id"]
                    self.log_test("Project Creation", True, f"Project '{data['title']}' created with ID: {self.project_id}")
                    return True
                else:
                    self.log_test("Project Creation", False, "Missing project data in response")
            else:
                self.log_test("Project Creation", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Project Creation", False, f"Exception: {str(e)}")
            
        return False
        
    def test_get_projects(self):
        """Test getting all projects endpoint"""
        print("\n=== Testing Get All Projects ===")
        
        if not self.auth_token:
            self.log_test("Get Projects", False, "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/projects")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Projects", True, f"Retrieved {len(data)} projects")
                    return True
                else:
                    self.log_test("Get Projects", False, "Response is not a list")
            else:
                self.log_test("Get Projects", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Projects", False, f"Exception: {str(e)}")
            
        return False
        
    def test_get_specific_project(self):
        """Test getting specific project endpoint"""
        print("\n=== Testing Get Specific Project ===")
        
        if not self.auth_token or not self.project_id:
            self.log_test("Get Specific Project", False, "No auth token or project ID available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/projects/{self.project_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == self.project_id:
                    self.log_test("Get Specific Project", True, f"Retrieved project: {data['title']}")
                    return True
                else:
                    self.log_test("Get Specific Project", False, "Project ID mismatch in response")
            else:
                self.log_test("Get Specific Project", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Specific Project", False, f"Exception: {str(e)}")
            
        return False
        
    def test_create_task(self):
        """Test task creation endpoint"""
        print("\n=== Testing Task Creation ===")
        
        if not self.auth_token or not self.project_id:
            self.log_test("Task Creation", False, "No auth token or project ID available")
            return False
            
        task_data = {
            "title": "Design User Interface",
            "description": "Create wireframes and mockups for the mobile app user interface",
            "project_id": self.project_id,
            "status": "To Do"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/tasks", json=task_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "title" in data:
                    self.task_id = data["id"]
                    self.log_test("Task Creation", True, f"Task '{data['title']}' created with ID: {self.task_id}")
                    return True
                else:
                    self.log_test("Task Creation", False, "Missing task data in response")
            else:
                self.log_test("Task Creation", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Task Creation", False, f"Exception: {str(e)}")
            
        return False
        
    def test_get_tasks_for_project(self):
        """Test getting tasks for a specific project"""
        print("\n=== Testing Get Tasks for Project ===")
        
        if not self.auth_token or not self.project_id:
            self.log_test("Get Tasks for Project", False, "No auth token or project ID available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/tasks?project_id={self.project_id}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Tasks for Project", True, f"Retrieved {len(data)} tasks for project")
                    return True
                else:
                    self.log_test("Get Tasks for Project", False, "Response is not a list")
            else:
                self.log_test("Get Tasks for Project", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Tasks for Project", False, f"Exception: {str(e)}")
            
        return False
        
    def test_update_task_status(self):
        """Test updating task status endpoint"""
        print("\n=== Testing Update Task Status ===")
        
        if not self.auth_token or not self.task_id:
            self.log_test("Update Task Status", False, "No auth token or task ID available")
            return False
            
        status_data = {
            "status": "In Progress"
        }
        
        try:
            response = self.session.put(f"{BACKEND_URL}/tasks/{self.task_id}/status", json=status_data)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "In Progress":
                    self.log_test("Update Task Status", True, f"Task status updated to: {data['status']}")
                    return True
                else:
                    self.log_test("Update Task Status", False, "Status not updated correctly")
            else:
                self.log_test("Update Task Status", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Update Task Status", False, f"Exception: {str(e)}")
            
        return False
        
    def test_delete_task(self):
        """Test task deletion endpoint"""
        print("\n=== Testing Task Deletion ===")
        
        if not self.auth_token or not self.task_id:
            self.log_test("Task Deletion", False, "No auth token or task ID available")
            return False
            
        try:
            response = self.session.delete(f"{BACKEND_URL}/tasks/{self.task_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Task Deletion", True, "Task deleted successfully")
                    return True
                else:
                    self.log_test("Task Deletion", False, "No confirmation message in response")
            else:
                self.log_test("Task Deletion", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Task Deletion", False, f"Exception: {str(e)}")
            
        return False
        
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        print("\n=== Testing Unauthorized Access ===")
        
        # Remove auth header temporarily
        original_headers = self.session.headers.copy()
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
            
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me")
            
            if response.status_code == 401:
                self.log_test("Unauthorized Access", True, "Properly rejected unauthorized request")
                success = True
            else:
                self.log_test("Unauthorized Access", False, f"Expected 401, got {response.status_code}")
                success = False
                
        except Exception as e:
            self.log_test("Unauthorized Access", False, f"Exception: {str(e)}")
            success = False
            
        # Restore auth header
        self.session.headers.update(original_headers)
        return success
        
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting Backend API Tests for Project Management App")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Authentication tests
        if not self.test_user_registration():
            print("❌ Registration failed, trying login with existing user...")
            if not self.test_user_login():
                print("❌ Both registration and login failed. Cannot continue.")
                return False
                
        self.test_get_user_profile()
        self.test_unauthorized_access()
        
        # Project management tests
        self.test_create_project()
        self.test_get_projects()
        self.test_get_specific_project()
        
        # Task management tests
        self.test_create_task()
        self.test_get_tasks_for_project()
        self.test_update_task_status()
        self.test_delete_task()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
                    
        print("\n" + "=" * 60)

if __name__ == "__main__":
    tester = ProjectManagementTester()
    tester.run_all_tests()