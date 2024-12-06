from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing


class ChangeAnswersBehavior(TaskSet):
    def on_start(self):
        self.change_answers()

    def login(self):
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/login", data={
            "email": 'user1@example.com',
            "password": '1234',
            "csrf_token": csrf_token
        })

    @task
    def change_answers(self):
        response = self.client.get("/profile/edit_answers")
        if response.status_code != 200 or "Establish your Security Answers" not in response.text:
            print("Not logged in or unexpected response, redirecting to login")
            self.login()
            response = self.client.get("/profile/edit_answers")

        csrf_token = get_csrf_token(response)
        response = self.client.post("/profile/edit_answers", data={
            "answer1": 'Fluffy',
            "answer2": 'Mr. Smith',
            "answer3": 'Soccer',
            "csrf_token": csrf_token
        })


class ProfileUser(HttpUser):
    tasks = [ChangeAnswersBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
