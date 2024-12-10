import pytest

from app import db
from app.modules.fakenodo.models import Deposition
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType, Author
from app.modules.fakenodo.services import FakenodoService


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():

        deposition_test = Deposition(
            dep_metadata={"title": "Sample Dataset 1", "description": "Description for dataset 1"}
        )
        db.session.add(deposition_test)
        db.session.commit()

    yield test_client


def test_get_deposition_succes(test_client):
    response = test_client.get("/fakenodo/1")
    assert response.status_code == 200


def test_get_deposition_fail_not_deposition(test_client):
    response = test_client.get("/fakenodo/50")
    assert response.status_code == 404


def test_get_deposition_service_succes(test_client):

    deposition = FakenodoService().get_deposition(1)

    assert deposition.dep_metadata == {"title": "Sample Dataset 1", "description": "Description for dataset 1"}


def test_create_deposition_service_success(test_client):

    ds_meta_data = DSMetaData(
        title="Test Dataset Title",
        description="This is a test dataset description.",
        publication_type=PublicationType.JOURNAL_ARTICLE,
        tags="test",
        authors=[
            Author(name="Tester", affiliation="Testing university", orcid="0000-0000-0000-0001"),
            Author(name="Probador", affiliation="University de pruebas", orcid="0000-0000-0000-0002"),
        ]
    )

    dataset = DataSet(ds_meta_data=ds_meta_data)

    deposition = FakenodoService().create_new_deposition(dataset, {})

    assert deposition.dep_metadata["title"] == "Test Dataset Title"
    assert deposition.dep_metadata["description"] == "This is a test dataset description."
    assert deposition.dep_metadata["models"] == {}
    assert deposition.dep_metadata["keywords"] == ["test", "uvlhub"]
    assert deposition.dep_metadata["access_right"] == "open"
    assert deposition.dep_metadata["license"] == "CC-BY-4.0"
    assert deposition.dep_metadata["upload_type"] == "publication"
    assert deposition.dep_metadata["publication_type"] == "article"
    assert deposition.dep_metadata["creators"] == [
        {
            "affiliation": "Testing university",
            "name": "Tester",
            "orcid": "0000-0000-0000-0001"
        },
        {
            "name": "Probador",
            "affiliation": "University de pruebas",
            "orcid": "0000-0000-0000-0002"
        }
    ]

    ds_meta_data2 = DSMetaData(
        title="Test Dataset Title",
        description="This is a test dataset description.",
        publication_type=PublicationType.NONE,
    )

    dataset2 = DataSet(ds_meta_data=ds_meta_data2)

    deposition2 = FakenodoService().create_new_deposition(dataset2, {})

    assert deposition2.dep_metadata["keywords"] == ["uvlhub"]
    assert deposition2.dep_metadata["upload_type"] == "dataset"
    assert not deposition2.dep_metadata["publication_type"]
