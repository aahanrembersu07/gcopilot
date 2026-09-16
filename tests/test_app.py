from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_signup_rejects_duplicate_email():
    activity_name = "Soccer Team"
    original_participants = activities[activity_name]["participants"][:]
    activities[activity_name]["participants"] = ["student@example.com"]

    try:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "student@example.com"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    finally:
        activities[activity_name]["participants"] = original_participants


def test_unregister_participant_removes_email():
    activity_name = "Basketball Club"
    original_participants = activities[activity_name]["participants"][:]
    activities[activity_name]["participants"] = ["first@example.com", "second@example.com"]

    try:
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": "first@example.com"},
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Removed first@example.com from Basketball Club"
        assert "first@example.com" not in activities[activity_name]["participants"]
        assert "second@example.com" in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants
