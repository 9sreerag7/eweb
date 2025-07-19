#!/usr/bin/env python3
"""
Additional Backend API Tests for Edge Cases and Error Handling
"""

import requests
import json

BACKEND_URL = "https://51e0177b-ba15-48c9-bc18-7c7581855d01.preview.emergentagent.com/api"

def test_duplicate_registration():
    """Test duplicate user registration"""
    print("=== Testing Duplicate Registration ===")
    
    user_data = {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@projectmanager.com",
        "password": "SecurePass123!",
        "role": "Manager"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=user_data)
    
    if response.status_code == 400:
        print("✅ PASS: Duplicate registration properly rejected")
        return True
    else:
        print(f"❌ FAIL: Expected 400, got {response.status_code}")
        return False

def test_invalid_login():
    """Test login with invalid credentials"""
    print("=== Testing Invalid Login ===")
    
    login_data = {
        "email": "sarah.johnson@projectmanager.com",
        "password": "WrongPassword123!"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code == 401:
        print("✅ PASS: Invalid login properly rejected")
        return True
    else:
        print(f"❌ FAIL: Expected 401, got {response.status_code}")
        return False

def test_access_nonexistent_project():
    """Test accessing a non-existent project"""
    print("=== Testing Non-existent Project Access ===")
    
    # First login to get token
    login_data = {
        "email": "sarah.johnson@projectmanager.com",
        "password": "SecurePass123!"
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print("❌ FAIL: Could not login for test")
        return False
        
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to access non-existent project
    fake_project_id = "non-existent-project-id"
    response = requests.get(f"{BACKEND_URL}/projects/{fake_project_id}", headers=headers)
    
    if response.status_code == 404:
        print("✅ PASS: Non-existent project properly returns 404")
        return True
    else:
        print(f"❌ FAIL: Expected 404, got {response.status_code}")
        return False

def test_create_task_invalid_project():
    """Test creating task with invalid project ID"""
    print("=== Testing Task Creation with Invalid Project ===")
    
    # First login to get token
    login_data = {
        "email": "sarah.johnson@projectmanager.com",
        "password": "SecurePass123!"
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print("❌ FAIL: Could not login for test")
        return False
        
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create task with invalid project ID
    task_data = {
        "title": "Invalid Task",
        "description": "This should fail",
        "project_id": "invalid-project-id",
        "status": "To Do"
    }
    
    response = requests.post(f"{BACKEND_URL}/tasks", json=task_data, headers=headers)
    
    if response.status_code == 404:
        print("✅ PASS: Task creation with invalid project properly rejected")
        return True
    else:
        print(f"❌ FAIL: Expected 404, got {response.status_code}")
        return False

def run_additional_tests():
    """Run all additional tests"""
    print("🔍 Running Additional Backend API Tests")
    print("=" * 50)
    
    results = []
    results.append(test_duplicate_registration())
    results.append(test_invalid_login())
    results.append(test_access_nonexistent_project())
    results.append(test_create_task_invalid_project())
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print("📊 ADDITIONAL TESTS SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

if __name__ == "__main__":
    run_additional_tests()