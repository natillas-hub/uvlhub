import pytest

from app import db
from app.modules.dataset.models import DataSet, DSMetrics, DSMetaData, PublicationType
from app.modules.featuremodel.models import FeatureModel
from app.modules.hubfile.models import Hubfile
from app.modules.dataset.services import DataSetService 



@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():

        ds_metrics_test = DSMetrics(
            number_of_models="5",
            number_of_features="20"
        )
        ds_meta_data_test = DSMetaData(
            deposition_id=123456,
            title="Test Dataset Title",
            description="This is a test dataset description.",
            publication_type=PublicationType.JOURNAL_ARTICLE,
            publication_doi="10.1234/test.doi",
            dataset_doi="10.1234/dataset.doi",
            tags="test, dataset, example",
            ds_metrics=ds_metrics_test
        )
        db.session.add_all([ds_metrics_test, ds_meta_data_test])

        dataset_test = DataSet(
            user_id=1,
            ds_meta_data_id=1
        )
        db.session.add(dataset_test)

        feature_model_test = FeatureModel(
            data_set_id=1
        )
        db.session.add(feature_model_test)
        db.session.commit()

        hubfile1 = Hubfile(
            name="file1.uvl",
            checksum="abc123",
            size=1024,
            feature_model_id=1
        )
        hubfile2 = Hubfile(
            name="file2.uvl",
            checksum="def456",
            size=2048,
            feature_model_id=1
        )
        hubfile3 = Hubfile(
            name="file3.uvl",
            checksum="ghi789",
            size=4096,
            feature_model_id=1
        )
        db.session.add_all([hubfile1, hubfile2, hubfile3])
        db.session.commit()

    yield test_client


def test_download_dataset_succesful(test_client):
    response = test_client.get("/dataset/download/1/UVL")
    assert response.status_code == 200
    response = test_client.get("/dataset/download/1/DIMACS")
    assert response.status_code == 200
    response = test_client.get("/dataset/download/1/SPLOT")
    assert response.status_code == 200
    response = test_client.get("/dataset/download/1/GLENCOE")
    assert response.status_code == 200


def test_download_dataset_wrong_format(test_client):
    response = test_client.get("/dataset/download/1/WRONG")
    assert response.status_code == 400
    assert response.json == {"error": "Formato de descarga no soportado"}


def test_download_dataset_no_dataset(test_client):
    response = test_client.get("/dataset/download/3/UVL")
    assert response.status_code == 404

# Tests unitarios para la feature 2
def test_user_datasets_single_user(test_client):
    """
    Verifica que se obtienen correctamente los datasets de un único usuario.
    """
    dataset_service = DataSetService()
    user_id = 1

    datasets = dataset_service.get_datasets_by_user(user_id)

    # Según los datos de test_client, el usuario con id=1 tiene un dataset.
    assert len(datasets) == 1
    assert all(dataset.user_id == user_id for dataset in datasets)
    assert datasets[0].ds_meta_data.title == "Test Dataset Title"


def test_user_datasets_no_datasets(test_client):
    """
    Verifica que un usuario sin datasets no genera resultados.
    """
    dataset_service = DataSetService()
    user_id = 999  # Usuario inexistente en los datos del test_client

    datasets = dataset_service.get_datasets_by_user(user_id)

    assert len(datasets) == 0


def test_user_datasets_multiple_users(test_client):
    """
    Verifica que no se mezclan datasets entre usuarios diferentes.
    """
    dataset_service = DataSetService()
    user_id = 2

    # No hay datasets creados para user_id=2 en los datos del test_client
    datasets = dataset_service.get_datasets_by_user(user_id)

    assert len(datasets) == 0


def test_user_datasets_invalid_user_id(test_client):
    """
    Verifica que la función maneja IDs de usuario no válidos devolviendo una lista vacía.
    """
    dataset_service = DataSetService()
    user_id = None

    datasets = dataset_service.get_datasets_by_user(user_id)
    assert len(datasets) == 0

