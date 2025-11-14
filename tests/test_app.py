"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for getting activities"""

    def test_get_activities_returns_200(self):
        """Test that /activities endpoint returns 200 status"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that response contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Swimming Club",
            "Art Studio",
            "Drama Club",
            "Math Olympiad",
            "Science Club"
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for signing up for activities"""

    def test_signup_returns_200_for_valid_request(self):
        """Test that signup returns 200 for valid request"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@example.com"
        )
        assert response.status_code == 200

    def test_signup_returns_message(self):
        """Test that signup returns success message"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@example.com"
        )
        data = response.json()
        assert "message" in data
        assert "newstudent@example.com" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_for_nonexistent_activity_returns_404(self):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student_returns_400(self):
        """Test that signing up twice returns 400"""
        email = "duplicate@example.com"
        
        # First signup
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Duplicate signup
        response2 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for unregistering from activities"""

    def test_unregister_returns_200_for_registered_participant(self):
        """Test that unregister returns 200 for registered participant"""
        email = "unregister_test@example.com"
        
        # First signup
        client.post(f"/activities/Programming Class/signup?email={email}")
        
        # Then unregister
        response = client.post(
            f"/activities/Programming Class/unregister?email={email}"
        )
        assert response.status_code == 200

    def test_unregister_returns_message(self):
        """Test that unregister returns success message"""
        email = "unregister_msg@example.com"
        
        # First signup
        client.post(f"/activities/Gym Class/signup?email={email}")
        
        # Then unregister
        response = client.post(
            f"/activities/Gym Class/unregister?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Gym Class" in data["message"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregister from nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_unregistered_participant_returns_400(self):
        """Test that unregistering non-participant returns 400"""
        response = client.post(
            "/activities/Basketball Team/unregister?email=notregistered@example.com"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_removes_participant_from_list(self):
        """Test that unregister actually removes participant from list"""
        email = "remove_test@example.com"
        activity = "Swimming Club"
        
        # Get initial participant count
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity]["participants"])
        
        # Signup
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify participant was added
        response_after_signup = client.get("/activities")
        count_after_signup = len(response_after_signup.json()[activity]["participants"])
        assert count_after_signup == count_before + 1
        
        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Verify participant was removed
        response_after_unregister = client.get("/activities")
        count_after_unregister = len(response_after_unregister.json()[activity]["participants"])
        assert count_after_unregister == count_before


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_redirects_to_static_index(self):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
