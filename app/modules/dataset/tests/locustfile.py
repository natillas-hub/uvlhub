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
    # Tests de Locust para probar la feature de Download All
    @task
    def download_all_uvl(self):
        # Prueba la funcionalidad download_all en formato UVL
        response = self.client.get("/dataset/download_all", params={"format": "UVL"})
        if response.status_code == 200:
            print("Download all datasets successful.")
        elif response.status_code == 404:
            print("No datasets available for download.")
        else:
            print(f"Error in download all: {response.status_code}")
    @task
    def download_all_dimacs(self):
        # Prueba la funcionalidad download_all en formato DIMACS
        response = self.client.get("/dataset/download_all", params={"format": "DIMACS"})
        if response.status_code == 200:
            print("Download all datasets successful.")
        elif response.status_code == 404:
            print("No datasets available for download.")
        else:
            print(f"Error in download all: {response.status_code}")
    @task
    def download_all_glencoe(self):
        # Prueba la funcionalidad download_all en formato GLENCOE
        response = self.client.get("/dataset/download_all", params={"format": "GLENCOE"})
        if response.status_code == 200:
            print("Download all datasets successful.")
        elif response.status_code == 404:
            print("No datasets available for download.")
        else:
            print(f"Error in download all: {response.status_code}")
    @task
    def download_all_splot(self):
        # Prueba la funcionalidad download_all en formato SPLOT
        response = self.client.get("/dataset/download_all", params={"format": "SPLOT"})
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
