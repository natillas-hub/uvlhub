from app.modules.fakenodo.models import Deposition
from core.seeders.BaseSeeder import BaseSeeder


class FakenodoSeeder(BaseSeeder):

    def run(self):
        depositions = [
            Deposition(
                dep_metadata={"title": "Sample Dataset 1", "description": "Description for dataset 1"},
            ),
            Deposition(
                dep_metadata={"title": "Sample Dataset 2", "description": "Description for dataset 2"},
            ),
            Deposition(
                dep_metadata={"title": "Sample Dataset 3", "description": "Description for dataset 3"},
            ),
            Deposition(
                dep_metadata={"title": "Sample Dataset 4", "description": "Description for dataset 4"},
            )
        ]
        self.seed(depositions)
