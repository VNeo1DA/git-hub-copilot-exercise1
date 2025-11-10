from fastapi.testclient import TestClient
from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Sanity check: activities fixture contains known keys
    assert "Chess Club" in data


def test_signup_and_unregister_participant():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure test email is not present initially
    assert email not in activities[activity]["participants"]

    # Sign up
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_resp.status_code == 200
    assert f"Signed up {email}" in signup_resp.json().get("message", "")

    # Now the activity should include the new participant
    get_resp = client.get("/activities")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert email in data[activity]["participants"]

    # Unregister
    del_resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert del_resp.status_code == 200
    assert f"Unregistered {email}" in del_resp.json().get("message", "")

    # Confirm removal
    get_resp2 = client.get("/activities")
    data2 = get_resp2.json()
    assert email not in data2[activity]["participants"]


def test_signup_duplicate_returns_400():
    activity = "Programming Class"
    email = "duplicate@example.com"

    # Ensure clean start: remove if present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # First signup should succeed
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    # Second signup should fail with 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # Cleanup
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)
