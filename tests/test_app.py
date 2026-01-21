"""
Tests for the Mergington High School Activities API
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original_activities = {
        "Soccer": {
            "description": "Competitive soccer team and training",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu"]
        },
        "Basketball": {
            "description": "Basketball league and skills development",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture classes",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Experiments, research projects, and STEM activities",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 22,
            "participants": ["mia@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_activities(self, client, reset_activities):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "Soccer" in data
        assert "Basketball" in data
        assert len(data) == 9
        
        # Verify Soccer structure
        assert data["Soccer"]["description"] == "Competitive soccer team and training"
        assert data["Soccer"]["max_participants"] == 18
        assert "alex@mergington.edu" in data["Soccer"]["participants"]


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant for an activity"""
        response = client.post(
            "/activities/Soccer/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Soccer" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Soccer"]["participants"]
    
    def test_signup_already_registered_participant(self, client, reset_activities):
        """Test signing up a participant who is already registered"""
        response = client.post(
            "/activities/Soccer/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_participant(self, client, reset_activities):
        """Test unregistering a participant from an activity"""
        response = client.post(
            "/activities/Soccer/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "Unregistered alex@mergington.edu from Soccer" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "alex@mergington.edu" not in activities["Soccer"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client, reset_activities):
        """Test unregistering a participant who is not registered"""
        response = client.post(
            "/activities/Soccer/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered for this activity" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/NonexistentActivity/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for the root / endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestIntegration:
    """Integration tests for complex scenarios"""
    
    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test the complete flow of signing up and then unregistering"""
        # Sign up
        signup_response = client.post(
            "/activities/Drama Club/signup?email=testuser@mergington.edu"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "testuser@mergington.edu" in activities["Drama Club"]["participants"]
        initial_count = len(activities["Drama Club"]["participants"])
        
        # Unregister
        unregister_response = client.post(
            "/activities/Drama Club/unregister?email=testuser@mergington.edu"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "testuser@mergington.edu" not in activities["Drama Club"]["participants"]
        assert len(activities["Drama Club"]["participants"]) == initial_count - 1
