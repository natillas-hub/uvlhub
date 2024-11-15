from app.modules.explore.repositories import ExploreRepository
from core.services.BaseService import BaseService


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(self, query="", sorting="newest", publication_type="any", 
               min_features=None, max_features=None, min_products=None, max_products=None, **kwargs):
        return self.repository.filter(
            query=query,
            sorting=sorting,
            publication_type=publication_type,
            min_features=min_features,
            max_features=max_features,
            min_products=min_products,
            max_products=max_products,
            **kwargs
        )
