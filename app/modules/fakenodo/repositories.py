from app.modules.fakenodo.models import Deposition
from core.repositories.BaseRepository import BaseRepository


class DepositionRepo(BaseRepository):
    def __init__(self):
        super().__init__(Deposition)

    def get_by_id(self, id):
        deposition = super().get_by_id(id)
        return deposition

    def create_new_deposition(self, metadata):
        return self.create(metadata=metadata)
