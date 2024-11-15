from app.modules.explore.repositories import ExploreRepository
from core.services.BaseService import BaseService


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(self, query="", sorting="newest", publication_type="any", 
               min_features=None, max_features=None, min_products=None, max_products=None, **kwargs):
        # Validar sorting
        if sorting not in ["newest", "oldest"]:
            sorting = "newest"
        
        # Validar rangos
        if min_features is not None and max_features is not None:
            if min_features > max_features:
                raise ValueError("min_features cannot be greater than max_features")
                
        if min_products is not None and max_products is not None:
            if min_products > max_products:
                raise ValueError("min_products cannot be greater than max_products")
                
        # Validar valores negativos
        if (min_features is not None and min_features < 0) or \
           (max_features is not None and max_features < 0) or \
           (min_products is not None and min_products < 0) or \
           (max_products is not None and max_products < 0):
            raise ValueError("Feature and product counts cannot be negative")

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
