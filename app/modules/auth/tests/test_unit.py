import pytest
from flask import url_for

from app import db
from app.modules.auth.services import AuthenticationService
from app.modules.auth.repositories import UserRepository
from app.modules.profile.repositories import UserProfileRepository
from app.modules.auth.services import PasswordResetService
from app.modules.auth.models import User


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(
            email='user@example.com',
            password='test1234',
            security_answer1="answer1",
            security_answer2="answer2",
            security_answer3="answer3")
        db.session.add(user_test)
        db.session.commit()
    yield test_client


def test_login_success(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path != url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_email(test_client):
    response = test_client.post(
        "/login", data=dict(email="bademail@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_password(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="basspassword"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_signup_user_no_name(test_client):
    response = test_client.post(
        "/signup", data=dict(surname="Foo", email="test@example.com", password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert b"This field is required" in response.data, response.data


def test_signup_user_unsuccessful(test_client):
    email = "test@example.com"
    response = test_client.post(
        "/signup", data=dict(name="Test", surname="Foo", email=email, password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert f"Email {email} in use".encode("utf-8") in response.data


def test_signup_user_successful(test_client):
    response = test_client.post(
        "/signup",
        data=dict(name="Foo", surname="Example", email="foo@example.com", password="foo1234"),
        follow_redirects=True,
    )
    assert response.request.path == url_for("public.index"), "Signup was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_reset_password_successful(test_client):
    response = test_client.post(
        "/reset_password",
        data=dict(
            email="user@example.com",
            answer1="answer1",
            answer2="answer2",
            answer3="answer3",
            new_password="newpassword"),
        follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Reset password was unsuccessful"


def test_reset_password_unsuccessful_bad_answer(test_client):
    response = test_client.post(
        "/reset_password",
        data=dict(
            email="user@example.com",
            answer1="wrong",
            answer2="answer2",
            answer3="answer3",
            new_password="newpassword"),
        follow_redirects=True
    )

    assert response.request.path != url_for("auth.login"), "Reset password was unsuccessful"
    assert "Incorrect answers to security questions.".encode("utf-8") in response.data


def test_reset_password_unsuccessful_bad_email(test_client):
    response = test_client.post(
        "/reset_password",
        data=dict(
            email="bademail@example.com",
            answer1="wrong",
            answer2="answer2",
            answer3="answer3",
            new_password="newpassword"),
        follow_redirects=True
    )

    assert response.request.path != url_for("auth.login"), "Reset password was unsuccessful"
    assert "No user found with that email.".encode("utf-8") in response.data


def test_service_create_with_profie_success(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "service_test@example.com",
        "password": "test1234"
    }

    AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 1
    assert UserProfileRepository().count() == 1


def test_service_create_with_profile_fail_no_email(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "",
        "password": "1234"
    }

    with pytest.raises(ValueError, match="Email is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_service_create_with_profile_fail_no_password(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "test@example.com",
        "password": ""
    }

    with pytest.raises(ValueError, match="Password is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_service_password_reset_success(clean_database):
    user_data = {
        "email": "user@example.com",
        "password": "oldpassword",
        "security_answer1": "answer1",
        "security_answer2": "answer2",
        "security_answer3": "answer3"
    }
    user = User(**user_data)
    db.session.add(user)
    db.session.commit()

    service = PasswordResetService()
    result = service.reset_password("user@example.com", "answer1", "answer2", "answer3", "newpassword")
    assert result == "Password updated successfully."
    updated_user = UserRepository().get_by_email("user@example.com")
    assert updated_user.check_password("newpassword")


def test_service_reset_password_bad_email(clean_database):
    service = PasswordResetService()
    result = service.reset_password("bademail@example.com", "answer1", "answer2", "answer3", "newpassword")

    assert result == "No user found with that email."


def test_service_reset_password_incorrect_answers(clean_database):
    user_data = {
        "email": "user@example.com",
        "password": "oldpassword",
        "security_answer1": "answer1",
        "security_answer2": "answer2",
        "security_answer3": "answer3"
    }
    user = User(**user_data)
    db.session.add(user)
    db.session.commit()

    service = PasswordResetService()
    result = service.reset_password("user@example.com", "wronganswer1", "wronganswer2", "wronganswer3", "newpassword")

    assert result == "Incorrect answers to security questions."
    updated_user = UserRepository().get_by_email("user@example.com")
    assert updated_user.check_password("oldpassword")


def test_service_reset_password_not_configured_security(clean_database):
    user_data = {
        "email": "user@example.com",
        "password": "oldpassword"
    }
    user = User(**user_data)
    db.session.add(user)
    db.session.commit()

    service = PasswordResetService()
    result = service.reset_password("user@example.com", "wronganswer1", "wronganswer2", "wronganswer3", "newpassword")

    assert result == "Incorrect answers to security questions."
    updated_user = UserRepository().get_by_email("user@example.com")
    assert updated_user.check_password("oldpassword")
