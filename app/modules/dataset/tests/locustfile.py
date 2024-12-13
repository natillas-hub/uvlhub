from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing
from app.modules.dataset.models import PublicationType


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

    @task
    def download_uvl(self):
        response = self.client.get("/dataset/download/1", params={"format": "UVL"})
        if response.status_code == 200:
            print("Download dataset successful.")
        elif response.status_code == 404:
            print("Dataset no available for download.")
        else:
            print(f"Error in download splot: {response.status_code}")

    @task
    def download_glecone(self):
        response = self.client.get("/dataset/download/1", params={"format": "Glecone"})
        if response.status_code == 200:
            print("Download dataset successful.")
        elif response.status_code == 404:
            print("Dataset no available for download.")
        else:
            print(f"Error in download splot: {response.status_code}")

    @task
    def download_dimacs(self):
        response = self.client.get("/dataset/download/1", params={"format": "Dimacs"})
        if response.status_code == 200:
            print("Download dataset successful.")
        elif response.status_code == 404:
            print("Dataset no available for download.")
        else:
            print(f"Error in download splot: {response.status_code}")

    @task
    def download_splot(self):
        response = self.client.get("/dataset/download/1", params={"format": "SPLOT"})
        if response.status_code == 200:
            print("Download dataset successful.")
        elif response.status_code == 404:
            print("Dataset no available for download.")
        else:
            print(f"Error in download splot: {response.status_code}")


class DatasetEditBehavior(TaskSet):
    def on_start(self):
        self.login()

    def login(self):
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/login", data={
            "email": 'user1@example.com',
            "password": '1234',
            "csrf_token": csrf_token
        })

    @task
    def test_edit_draft(self):
        response = self.client.get("/dataset/edit/5")
        csrf_token = get_csrf_token(response)
        form_data = {
            'title': 'title',
            'desc': 'Test Description',
            'publication_type': PublicationType.JOURNAL_ARTICLE.value,
            'publication_doi': 'https://prueba.com',
            'tags': 'test, dataset, example',
            'csrf_token': csrf_token
        }

        response = self.client.post('/dataset/edit/5', data=form_data)


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior, DatasetEditBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
