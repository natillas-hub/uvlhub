from app.modules.fakenodo.repositories import DepositionRepo
from core.services.BaseService import BaseService


class FakenodoService(BaseService):
    def __init__(self):
        self.deposition_repository = DepositionRepo()

    def get_deposition(self, id):
        return self.deposition_repository.get_by_id(id)

    def create_new_deposition(self, dataset):
        ds_meta_data = dataset.ds_meta_data
        metadataJSON = {
            "title": ds_meta_data.title,
            "upload_type": "dataset" if ds_meta_data.publication_type.value == "none" else "publication",
            "publication_type": (
                ds_meta_data.publication_type.value
                if ds_meta_data.publication_type.value != "none"
                else None
            ),
            "description": ds_meta_data.description,
            "creators": [
                {
                    "name": author.name,
                    **({"affiliation": author.affiliation} if author.affiliation else {}),
                    **({"orcid": author.orcid} if author.orcid else {}),
                }
                for author in ds_meta_data.authors
            ],
            "keywords": (
                ["uvlhub"] if not ds_meta_data.tags else ds_meta_data.tags.split(", ") + ["uvlhub"]
            ),
            "access_right": "open",
            "license": "CC-BY-4.0",
        }

        return self.deposition_repository.create(
                dep_metadata=metadataJSON
            )
