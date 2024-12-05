from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing
import random


class ExploreBehavior(TaskSet):
    def on_start(self):
        self.index()

    @task(1)
    def index(self):
        """Test de acceso a la página principal"""
        with self.client.get("/explore", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Explore index failed: {response.status_code}")
            else:
                response.success()

    @task(2)
    def basic_search(self):
        """Búsqueda básica sin filtros"""
        payload = {
            'query': '',
            'publication_type': 'any',
            'sorting': 'newest',
            'min_features': None,
            'max_features': None,
            'min_products': None,
            'max_products': None
        }
        with self.client.post("/explore", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Basic search failed: {response.status_code}")
            else:
                response.success()

    @task(2)
    def search_with_query(self):
        """Búsqueda con términos específicos"""
        queries = ['Test Integration', 'test', 'data', 'research']
        payload = {
            'query': random.choice(queries),
            'publication_type': 'any',
            'sorting': 'newest'
        }
        with self.client.post("/explore", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Query search failed: {response.status_code}")
            else:
                response.success()

    @task(2)
    def search_with_publication_type(self):
        """Búsqueda filtrando por tipo de publicación"""
        types = ['article', 'dataset', 'any']
        payload = {
            'query': '',
            'publication_type': random.choice(types),
            'sorting': 'newest'
        }
        with self.client.post("/explore", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Publication type search failed: {response.status_code}")
            else:
                response.success()

    @task(2)
    def search_with_sorting(self):
        """Búsqueda con diferentes ordenamientos"""
        sorting_options = ['newest', 'oldest']
        payload = {
            'query': '',
            'publication_type': 'any',
            'sorting': random.choice(sorting_options)
        }
        with self.client.post("/explore", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Sorting search failed: {response.status_code}")
            else:
                response.success()

    @task(1)
    def search_with_feature_limits(self):
        """Búsqueda con límites de features"""
        payload = {
            'query': '',
            'publication_type': 'any',
            'sorting': 'newest',
            'min_features': random.randint(1, 50),
            'max_features': random.randint(51, 100)
        }
        with self.client.post("/explore", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Feature limits search failed: {response.status_code}")
            else:
                response.success()

    @task(1)
    def search_with_product_limits(self):
        """Búsqueda con límites de productos"""
        payload = {
            'query': '',
            'publication_type': 'any',
            'sorting': 'newest',
            'min_products': random.randint(1, 50),
            'max_products': random.randint(51, 100)
        }
        with self.client.post("/explore", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Product limits search failed: {response.status_code}")
            else:
                response.success()

    @task(1)
    def author_search(self):
        """Búsqueda por autor"""
        payload = {
            'query': 'Test Author',
            'publication_type': 'any',
            'sorting': 'newest'
        }
        with self.client.post("/explore", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Author search failed: {response.status_code}")
            else:
                response.success()


class ExploreUser(HttpUser):
    tasks = [ExploreBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()