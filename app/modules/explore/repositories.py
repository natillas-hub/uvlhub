import re
from sqlalchemy import any_, or_
import unidecode
from app.modules.dataset.models import Author, DSMetrics, DSMetaData, DataSet, PublicationType
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from core.repositories.BaseRepository import BaseRepository
from app import db
import logging

logger = logging.getLogger(__name__)


class ExploreRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def filter(
            self, query="", sorting="newest", publication_type="any",
            tags=[], min_features=None, max_features=None,
            min_products=None, max_products=None, **kwargs):
        # Normalize and remove unwanted characters
        normalized_query = unidecode.unidecode(query).lower()
        cleaned_query = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_query)

        filters = []
        for word in cleaned_query.split():
            filters.append(DSMetaData.title.ilike(f"%{word}%"))
            filters.append(DSMetaData.description.ilike(f"%{word}%"))
            filters.append(Author.name.ilike(f"%{word}%"))
            filters.append(Author.affiliation.ilike(f"%{word}%"))
            filters.append(Author.orcid.ilike(f"%{word}%"))
            filters.append(FMMetaData.uvl_filename.ilike(f"%{word}%"))
            filters.append(FMMetaData.title.ilike(f"%{word}%"))
            filters.append(FMMetaData.description.ilike(f"%{word}%"))
            filters.append(FMMetaData.publication_doi.ilike(f"%{word}%"))
            filters.append(FMMetaData.tags.ilike(f"%{word}%"))
            filters.append(DSMetaData.tags.ilike(f"%{word}%"))

        datasets = (
            self.model.query
            .join(DataSet.ds_meta_data)
            .join(DSMetaData.ds_metrics)
            .join(DSMetaData.authors)
            .join(DataSet.feature_models)
            .join(FeatureModel.fm_meta_data)
            .filter(or_(*filters))
            .filter(DSMetaData.dataset_doi.isnot(None))
        )

        if tags:
            datasets = datasets.filter(DSMetaData.tags.ilike(any_(f"%{tag}%" for tag in tags)))

        if publication_type != "any":
            matching_type = next(
                (member for member in PublicationType if member.value.lower() == publication_type), 
                None
            )
            if matching_type:
                datasets = datasets.filter(DSMetaData.publication_type == matching_type.name)

        # Aplicar filtros de features
        if min_features is not None:
            datasets = datasets.filter(
                db.cast(db.func.nullif(DSMetrics.number_of_features, ''), db.String).cast(db.Integer) >= min_features
            )

        if max_features is not None:
            datasets = datasets.filter(
                db.cast(db.func.nullif(DSMetrics.number_of_features, ''), db.String).cast(db.Integer) <= max_features
            )

        # Aplicar filtros de productos
        if min_products is not None:
            datasets = datasets.filter(
                db.cast(db.func.nullif(DSMetrics.number_of_models, ''), db.String).cast(db.Integer) >= min_products
            )

        if max_products is not None:
            datasets = datasets.filter(
                db.cast(db.func.nullif(DSMetrics.number_of_models, ''), db.String).cast(db.Integer) <= max_products
            )

        # Order by created_at
        if sorting == "oldest":
            datasets = datasets.order_by(self.model.created_at.asc())
        else:
            datasets = datasets.order_by(self.model.created_at.desc())

        return datasets.distinct().all()
