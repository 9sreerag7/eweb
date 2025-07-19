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
BACKEND_URL = "https://60777a23-ba2f-4025-8ff5-9b792169a72b.preview.emergentagent.com/api"

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

    def test_notifications_system(self):
        """Test complete notifications system"""
        print("\n=== Testing Notifications System ===")
        
        if not self.auth_token:
            self.log_test("Notifications System", False, "No auth token available")
            return False

        # First create a new task to generate notifications
        task_data = {
            "title": "Notification Test Task",
            "description": "Task created to test notification system",
            "project_id": self.project_id,
            "status": "To Do",
            "assigned_to": self.user_data["id"]  # Assign to self to trigger notification
        }
        
        try:
            # Create task (should generate notification)
            response = self.session.post(f"{BACKEND_URL}/tasks", json=task_data)
            if response.status_code != 200:
                self.log_test("Notifications System", False, f"Failed to create test task: {response.text}")
                return False
            
            test_task = response.json()
            test_task_id = test_task["id"]
            
            # Test 1: Create manual notification
            notification_data = {
                "user_id": self.user_data["id"],
                "title": "Test Notification",
                "message": "This is a test notification",
                "type": "test",
                "task_id": test_task_id,
                "project_id": self.project_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/notifications", json=notification_data)
            if response.status_code == 200:
                notification = response.json()
                self.log_test("Create Notification", True, f"Created notification: {notification['title']}")
                notification_id = notification["id"]
            else:
                self.log_test("Create Notification", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Test 2: Get all notifications
            response = self.session.get(f"{BACKEND_URL}/notifications")
            if response.status_code == 200:
                notifications = response.json()
                if isinstance(notifications, list) and len(notifications) > 0:
                    self.log_test("Get Notifications", True, f"Retrieved {len(notifications)} notifications")
                else:
                    self.log_test("Get Notifications", False, "No notifications found")
            else:
                self.log_test("Get Notifications", False, f"HTTP {response.status_code}: {response.text}")
            
            # Test 3: Get unread count
            response = self.session.get(f"{BACKEND_URL}/notifications/unread-count")
            if response.status_code == 200:
                count_data = response.json()
                if "count" in count_data:
                    self.log_test("Get Unread Count", True, f"Unread notifications: {count_data['count']}")
                else:
                    self.log_test("Get Unread Count", False, "Missing count in response")
            else:
                self.log_test("Get Unread Count", False, f"HTTP {response.status_code}: {response.text}")
            
            # Test 4: Mark notification as read
            response = self.session.put(f"{BACKEND_URL}/notifications/{notification_id}/read")
            if response.status_code == 200:
                self.log_test("Mark Notification Read", True, "Notification marked as read")
            else:
                self.log_test("Mark Notification Read", False, f"HTTP {response.status_code}: {response.text}")
            
            # Test 5: Test auto-notification on status change
            status_data = {"status": "In Progress"}
            response = self.session.put(f"{BACKEND_URL}/tasks/{test_task_id}/status", json=status_data)
            if response.status_code == 200:
                self.log_test("Auto-notification on Status Change", True, "Status updated (should generate notification)")
            else:
                self.log_test("Auto-notification on Status Change", False, f"Failed to update status: {response.text}")
            
            # Clean up test task
            self.session.delete(f"{BACKEND_URL}/tasks/{test_task_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Notifications System", False, f"Exception: {str(e)}")
            return False

    def test_file_attachments_system(self):
        """Test complete file attachments system"""
        print("\n=== Testing File Attachments System ===")
        
        if not self.auth_token or not self.project_id:
            self.log_test("File Attachments System", False, "No auth token or project ID available")
            return False

        # Create a test task for file attachments
        task_data = {
            "title": "File Attachment Test Task",
            "description": "Task created to test file attachment system",
            "project_id": self.project_id,
            "status": "To Do"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/tasks", json=task_data)
            if response.status_code != 200:
                self.log_test("File Attachments System", False, f"Failed to create test task: {response.text}")
                return False
            
            test_task = response.json()
            test_task_id = test_task["id"]
            
            # Test 1: Upload file (base64 encoded)
            import base64
            test_content = "This is a test file content for the project management system."
            encoded_content = base64.b64encode(test_content.encode()).decode()
            
            file_data = {
                "task_id": test_task_id,
                "filename": "test_document.txt",
                "content_type": "text/plain",
                "file_data": encoded_content
            }
            
            response = self.session.post(f"{BACKEND_URL}/files", json=file_data)
            if response.status_code == 200:
                file_attachment = response.json()
                self.log_test("Upload File", True, f"Uploaded file: {file_attachment['filename']}")
                file_id = file_attachment["id"]
            else:
                self.log_test("Upload File", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Test 2: Get files for task
            response = self.session.get(f"{BACKEND_URL}/files?task_id={test_task_id}")
            if response.status_code == 200:
                files = response.json()
                if isinstance(files, list) and len(files) > 0:
                    self.log_test("Get Files for Task", True, f"Retrieved {len(files)} files")
                else:
                    self.log_test("Get Files for Task", False, "No files found")
            else:
                self.log_test("Get Files for Task", False, f"HTTP {response.status_code}: {response.text}")
            
            # Test 3: Test file size validation (try to upload large file)
            large_content = "x" * (11 * 1024 * 1024)  # 11MB content
            large_encoded = base64.b64encode(large_content.encode()).decode()
            
            large_file_data = {
                "task_id": test_task_id,
                "filename": "large_file.txt",
                "content_type": "text/plain",
                "file_data": large_encoded
            }
            
            response = self.session.post(f"{BACKEND_URL}/files", json=large_file_data)
            if response.status_code == 400:
                self.log_test("File Size Validation", True, "Large file properly rejected")
            else:
                self.log_test("File Size Validation", False, f"Expected 400, got {response.status_code}")
            
            # Test 4: Delete file
            response = self.session.delete(f"{BACKEND_URL}/files/{file_id}")
            if response.status_code == 200:
                self.log_test("Delete File", True, "File deleted successfully")
            else:
                self.log_test("Delete File", False, f"HTTP {response.status_code}: {response.text}")
            
            # Clean up test task
            self.session.delete(f"{BACKEND_URL}/tasks/{test_task_id}")
            
            return True
            
        except Exception as e:
            self.log_test("File Attachments System", False, f"Exception: {str(e)}")
            return False

    def test_comments_system(self):
        """Test complete comments system with threading"""
        print("\n=== Testing Comments System ===")
        
        if not self.auth_token or not self.project_id:
            self.log_test("Comments System", False, "No auth token or project ID available")
            return False

        # Create a test task for comments
        task_data = {
            "title": "Comments Test Task",
            "description": "Task created to test comments system",
            "project_id": self.project_id,
            "status": "To Do"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/tasks", json=task_data)
            if response.status_code != 200:
                self.log_test("Comments System", False, f"Failed to create test task: {response.text}")
                return False
            
            test_task = response.json()
            test_task_id = test_task["id"]
            
            # Test 1: Create parent comment
            comment_data = {
                "task_id": test_task_id,
                "content": "This is a parent comment for testing the comments system."
            }
            
            response = self.session.post(f"{BACKEND_URL}/comments", json=comment_data)
            if response.status_code == 200:
                parent_comment = response.json()
                self.log_test("Create Parent Comment", True, f"Created comment: {parent_comment['content'][:50]}...")
                parent_comment_id = parent_comment["id"]
            else:
                self.log_test("Create Parent Comment", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Test 2: Create threaded (child) comment
            child_comment_data = {
                "task_id": test_task_id,
                "content": "This is a reply to the parent comment.",
                "parent_id": parent_comment_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/comments", json=child_comment_data)
            if response.status_code == 200:
                child_comment = response.json()
                self.log_test("Create Threaded Comment", True, f"Created reply comment with parent_id: {child_comment['parent_id']}")
                child_comment_id = child_comment["id"]
            else:
                self.log_test("Create Threaded Comment", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Test 3: Get all comments for task
            response = self.session.get(f"{BACKEND_URL}/comments?task_id={test_task_id}")
            if response.status_code == 200:
                comments = response.json()
                if isinstance(comments, list) and len(comments) >= 2:
                    self.log_test("Get Comments for Task", True, f"Retrieved {len(comments)} comments")
                else:
                    self.log_test("Get Comments for Task", False, f"Expected at least 2 comments, got {len(comments) if isinstance(comments, list) else 0}")
            else:
                self.log_test("Get Comments for Task", False, f"HTTP {response.status_code}: {response.text}")
            
            # Test 4: Update comment
            update_data = {
                "content": "This is an updated parent comment."
            }
            
            response = self.session.put(f"{BACKEND_URL}/comments/{parent_comment_id}", json=update_data)
            if response.status_code == 200:
                updated_comment = response.json()
                self.log_test("Update Comment", True, f"Updated comment content")
            else:
                self.log_test("Update Comment", False, f"HTTP {response.status_code}: {response.text}")
            
            # Test 5: Delete comment
            response = self.session.delete(f"{BACKEND_URL}/comments/{child_comment_id}")
            if response.status_code == 200:
                self.log_test("Delete Comment", True, "Comment deleted successfully")
            else:
                self.log_test("Delete Comment", False, f"HTTP {response.status_code}: {response.text}")
            
            # Clean up remaining comment and test task
            self.session.delete(f"{BACKEND_URL}/comments/{parent_comment_id}")
            self.session.delete(f"{BACKEND_URL}/tasks/{test_task_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Comments System", False, f"Exception: {str(e)}")
            return False

    def test_analytics_system(self):
        """Test progress analytics system"""
        print("\n=== Testing Analytics System ===")
        
        if not self.auth_token or not self.project_id:
            self.log_test("Analytics System", False, "No auth token or project ID available")
            return False

        try:
            # Create some test tasks with different statuses for analytics
            test_tasks = [
                {"title": "Analytics Task 1", "status": "To Do"},
                {"title": "Analytics Task 2", "status": "In Progress"},
                {"title": "Analytics Task 3", "status": "Done"},
                {"title": "Analytics Task 4", "status": "To Do"}
            ]
            
            created_task_ids = []
            for task_data in test_tasks:
                task_data.update({
                    "description": "Task for analytics testing",
                    "project_id": self.project_id
                })
                
                response = self.session.post(f"{BACKEND_URL}/tasks", json=task_data)
                if response.status_code == 200:
                    created_task_ids.append(response.json()["id"])
            
            # Test 1: Get progress analytics per project
            response = self.session.get(f"{BACKEND_URL}/analytics/progress")
            if response.status_code == 200:
                progress_data = response.json()
                if isinstance(progress_data, list):
                    found_project = False
                    for project_progress in progress_data:
                        if project_progress["project_id"] == self.project_id:
                            found_project = True
                            stats = project_progress["stats"]
                            self.log_test("Get Progress Analytics", True, 
                                        f"Project stats - Total: {stats['total_tasks']}, "
                                        f"Completed: {stats['completed_tasks']}, "
                                        f"Rate: {stats['completion_rate']}%")
                            break
                    
                    if not found_project:
                        self.log_test("Get Progress Analytics", False, "Project not found in analytics")
                else:
                    self.log_test("Get Progress Analytics", False, "Response is not a list")
            else:
                self.log_test("Get Progress Analytics", False, f"HTTP {response.status_code}: {response.text}")
            
            # Test 2: Get overall analytics overview
            response = self.session.get(f"{BACKEND_URL}/analytics/overview")
            if response.status_code == 200:
                overview_data = response.json()
                required_fields = ["total_projects", "total_tasks", "completed_tasks", 
                                 "completion_rate", "status_distribution", "recent_tasks_trend"]
                
                if all(field in overview_data for field in required_fields):
                    self.log_test("Get Analytics Overview", True, 
                                f"Overview - Projects: {overview_data['total_projects']}, "
                                f"Tasks: {overview_data['total_tasks']}, "
                                f"Completion: {overview_data['completion_rate']}%")
                else:
                    missing_fields = [field for field in required_fields if field not in overview_data]
                    self.log_test("Get Analytics Overview", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Get Analytics Overview", False, f"HTTP {response.status_code}: {response.text}")
            
            # Clean up test tasks
            for task_id in created_task_ids:
                self.session.delete(f"{BACKEND_URL}/tasks/{task_id}")
            
            return True
            
        except Exception as e:
            self.log_test("Analytics System", False, f"Exception: {str(e)}")
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
        
        # NEW FEATURE TESTS
        print("\n" + "=" * 60)
        print("🆕 TESTING NEW FEATURES")
        print("=" * 60)
        
        # Test all new backend features
        self.test_notifications_system()
        self.test_file_attachments_system()
        self.test_comments_system()
        self.test_analytics_system()
        
        # Clean up - delete the test task last
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