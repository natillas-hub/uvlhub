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
        
        # Validar rangos de features
        if min_features is not None and max_features is not None:
            min_features = int(min_features)
            max_features = int(max_features)
            if min_features > max_features:
                return []  # Retornar lista vacía si el rango no es válido
            
        # Validar rangos de productos
        if min_products is not None and max_products is not None:
            min_products = int(min_products)
            max_products = int(max_products)
            if min_products > max_products:
                return []  # Retornar lista vacía si el rango no es válido
        
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