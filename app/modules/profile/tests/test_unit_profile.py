import pytest
from flask import url_for

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app.modules.profile.services import AnswersUpdateService
from app.modules.auth.repositories import UserRepository


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    for module testing (por example, new users)
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


def test_edit_profile_page_get(test_client):
    """
    Tests access to the profile editing page via a GET request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/edit")
    assert response.status_code == 200, "The profile editing page could not be accessed."
    assert b"Edit profile" in response.data, "The expected content is not present on the page"

    logout(test_client)


def test_edit_answers_page_get(test_client):

    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/edit_answers")
    assert response.status_code == 200, "The answers editing page could not be accessed."
    assert b"Answer the security questions" in response.data, "The expected content is not present on the page"

    logout(test_client)


def test_answers_update_page_post_succesful(test_client):

    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.post(
        "/profile/edit_answers",
        data=dict(
            answer1="answer1",
            answer2="answer2",
            answer3="answer3"),
        follow_redirects=True)
    assert response.status_code == 200, "The answers could not be changed."
    assert response.request.path == url_for("profile.edit_profile"), "Reset password was unsuccessful"

    logout(test_client)


def test_service_change_answers_successful(clean_database):

    user_data = {
        "email": "user@example.com",
        "password": "test1234",
        "security_answer1": "answer1",
        "security_answer2": "answer2",
        "security_answer3": "answer3"
    }
    user = User(**user_data)
    db.session.add(user)
    db.session.commit()

    service = AnswersUpdateService()
    result = service.change_answers(user, "newanswer1", "newanswer2", "newanswer3")
    assert result == "Security answers updated successfully."
    updated_user = UserRepository().get_by_email("user@example.com")
    assert updated_user.check_security_answer1("newanswer1")
    assert updated_user.check_security_answer2("newanswer2")
    assert updated_user.check_security_answer3("newanswer3")
