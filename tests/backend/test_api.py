import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_activity_catalog(reset_activities):
    # Arrange
    # No state setup required beyond the default app data.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Soccer Team" in payload
    assert payload["Soccer Team"]["max_participants"] == 18


def test_signup_for_activity_success(reset_activities):
    # Arrange
    activity_name = "Soccer Team"
    email = "newstudent@example.com"
    activities[activity_name]["participants"] = ["existing@example.com"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_email(reset_activities):
    # Arrange
    activity_name = "Soccer Team"
    email = "student@example.com"
    activities[activity_name]["participants"] = [email]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity(reset_activities):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.post(f"/activities/{unknown_activity}/signup", params={"email": "student@example.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_full_activity(reset_activities):
    # Arrange
    activity_name = "Math Olympiad"
    activities[activity_name]["participants"] = [f"student{i}@example.com" for i in range(10)]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": "newstudent@example.com"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_participant_removes_email(reset_activities):
    # Arrange
    activity_name = "Basketball Club"
    email = "first@example.com"
    activities[activity_name]["participants"] = [email, "second@example.com"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_participant_rejects_missing_email(reset_activities):
    # Arrange
    activity_name = "Basketball Club"
    activities[activity_name]["participants"] = ["existing@example.com"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": "missing@example.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
