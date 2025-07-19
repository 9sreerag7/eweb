#!/usr/bin/env python3
"""
Debug script for team management system
"""

import requests
import json

BACKEND_URL = "https://60777a23-ba2f-4025-8ff5-9b792169a72b.preview.emergentagent.com/api"

def debug_team_management():
    session = requests.Session()
    
    # 1. Register manager
    import time
    timestamp = str(int(time.time()))
    manager_data = {
        "name": "Debug Manager",
        "email": f"debug.manager.{timestamp}@test.com",
        "password": "DebugPass123!",
        "role": "Manager"
    }
    
    print("1. Registering manager...")
    response = session.post(f"{BACKEND_URL}/auth/register", json=manager_data)
    if response.status_code == 200:
        manager_token_data = response.json()
        manager_token = manager_token_data["access_token"]
        manager_user = manager_token_data["user"]
        session.headers.update({"Authorization": f"Bearer {manager_token}"})
        print(f"✅ Manager registered: {manager_user['name']} (ID: {manager_user['id']})")
    else:
        print(f"❌ Manager registration failed: {response.text}")
        return
    
    # 2. Create project
    project_data = {
        "title": "Debug Team Project",
        "description": "Project for debugging team management"
    }
    
    print("\n2. Creating project...")
    response = session.post(f"{BACKEND_URL}/projects", json=project_data)
    if response.status_code == 200:
        project = response.json()
        project_id = project["id"]
        print(f"✅ Project created: {project['title']} (ID: {project_id})")
        print(f"   Owner ID: {project['owner_id']}")
        print(f"   Team members: {project.get('team_members', [])}")
    else:
        print(f"❌ Project creation failed: {response.text}")
        return
    
    # 3. Register team member
    team_member_data = {
        "name": "Debug Team Member",
        "email": f"debug.teammember.{timestamp}@test.com",
        "password": "TeamPass123!",
        "role": "Team Member"
    }
    
    print("\n3. Registering team member...")
    response = session.post(f"{BACKEND_URL}/auth/register", json=team_member_data)
    if response.status_code == 200:
        team_member_token_data = response.json()
        team_member_user = team_member_token_data["user"]
        print(f"✅ Team member registered: {team_member_user['name']} (ID: {team_member_user['id']})")
    else:
        print(f"❌ Team member registration failed: {response.text}")
        return
    
    # 4. Add team member to project
    team_update_data = {
        "team_members": [team_member_user["id"]]
    }
    
    print("\n4. Adding team member to project...")
    response = session.put(f"{BACKEND_URL}/projects/{project_id}/team", json=team_update_data)
    if response.status_code == 200:
        updated_project = response.json()
        print(f"✅ Team updated successfully")
        print(f"   Project ID: {updated_project['id']}")
        print(f"   Owner ID: {updated_project['owner_id']}")
        print(f"   Team members: {updated_project.get('team_members', [])}")
    else:
        print(f"❌ Team update failed: {response.text}")
        return
    
    # 5. Login as team member
    team_member_login = {
        "email": team_member_user["email"],
        "password": "TeamPass123!"
    }
    
    print("\n5. Logging in as team member...")
    team_session = requests.Session()
    response = team_session.post(f"{BACKEND_URL}/auth/login", json=team_member_login)
    if response.status_code == 200:
        team_token_data = response.json()
        team_session.headers.update({"Authorization": f"Bearer {team_token_data['access_token']}"})
        logged_in_user = team_token_data["user"]
        print(f"✅ Team member logged in: {logged_in_user['name']} (ID: {logged_in_user['id']})")
    else:
        print(f"❌ Team member login failed: {response.text}")
        return
    
    # 6. Test accessible projects for team member
    print("\n6. Testing accessible projects for team member...")
    response = team_session.get(f"{BACKEND_URL}/projects/accessible")
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        accessible_projects = response.json()
        print(f"✅ Accessible projects retrieved: {len(accessible_projects)} projects")
        for proj in accessible_projects:
            print(f"   - Project: {proj['title']} (ID: {proj['id']}, Owner: {proj['owner_id']})")
            print(f"     Team members: {proj.get('team_members', [])}")
    else:
        print(f"❌ Failed to get accessible projects: {response.text}")
    
    # 7. Test direct project access
    print(f"\n7. Testing direct project access for team member...")
    response = team_session.get(f"{BACKEND_URL}/projects/{project_id}")
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")

if __name__ == "__main__":
    debug_team_management()