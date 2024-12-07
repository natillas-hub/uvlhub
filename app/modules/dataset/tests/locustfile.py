from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing


class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()

    @task
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)
    @task
    def download_all(self):
        # Prueba la funcionalidad download_all en formato UVL
        response = self.client.get("/dataset/download_all", params={"format": "UVL"})
        if response.status_code == 200:
            print("Download all datasets successful.")
        elif response.status_code == 404:
            print("No datasets available for download.")
        else:
            print(f"Error in download all: {response.status_code}")


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
