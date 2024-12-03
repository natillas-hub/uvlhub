import pytest
from app.modules.conftest import login, logout
from app import db
from app.modules.dataset.models import DataSet, DSMetrics, DSMetaData, PublicationType
from app.modules.featuremodel.models import FeatureModel
from app.modules.hubfile.models import Hubfile


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


def test_download_all_dataset_succesful(test_client):
    # Iniciar sesión
    login_response = login(test_client, "test@example.com", "test1234")
    assert login_response.status_code == 200, "Login fallido"

    # Realizar pruebas
    response = test_client.get("/dataset/download_all?format=UVL")
    assert response.status_code == 200
    response = test_client.get("/dataset/download_all?format=DIMACS")
    assert response.status_code == 200
    response = test_client.get("/dataset/download_all?format=SPLOT")
    assert response.status_code == 200
    response = test_client.get("/dataset/download_all?format=GLENCOE")
    assert response.status_code == 200

    # Cerrar sesión
    logout(test_client)


def test_download_all_dataset_wrong_format(test_client):
    # Iniciar sesión
    login_response = login(test_client, "test@example.com", "test1234")
    assert login_response.status_code == 200, "Login fallido"

    # Realizar prueba
    response = test_client.get("/dataset/download_all?format=WRONG")
    assert response.status_code == 400
    assert response.json == {"error": "Formato de descarga no soportado"}

    # Cerrar sesión
    logout(test_client)


def test_download_all_dataset_empty(test_client):
    """
    Prueba que verifica el comportamiento cuando se intenta descargar datasets
    que no contienen archivos.
    """
    # Iniciar sesión
    login_response = login(test_client, "test@example.com", "test1234")
    assert login_response.status_code == 200, "Login fallido"

    try:
        # Crear un dataset vacío (sin archivos)
        ds_metrics_test = DSMetrics(
            number_of_models="0",
            number_of_features="0"
        )
        db.session.add(ds_metrics_test)
        db.session.commit()

        ds_meta_data_test = DSMetaData(
            deposition_id=999999,
            title="Empty Dataset",
            description="Dataset without files for testing.",
            publication_type=PublicationType.JOURNAL_ARTICLE,
            publication_doi="10.1234/empty.doi",
            dataset_doi="10.1234/empty.dataset.doi",
            tags="empty, test",
            ds_metrics_id=ds_metrics_test.id
        )
        db.session.add(ds_meta_data_test)
        db.session.commit()

        empty_dataset = DataSet(
            user_id=1,
            ds_meta_data_id=ds_meta_data_test.id
        )
        db.session.add(empty_dataset)
        db.session.commit()

        # Probar la descarga en diferentes formatos
        formats = ["UVL", "DIMACS", "SPLOT", "GLENCOE"]
        for format in formats:
            response = test_client.get(f"/dataset/download_all?format={format}")
            assert response.status_code == 200
            assert len(response.data) > 0
            assert b"all_datasets.zip" in response.headers['Content-Disposition'].encode()

    finally:
        # Limpiar
        db.session.delete(empty_dataset)
        db.session.delete(ds_meta_data_test)
        db.session.delete(ds_metrics_test)
        db.session.commit()
        logout(test_client)


@pytest.fixture
def test_client_without_login(test_app):
    with test_app.test_client() as client:
        yield client


def test_download_all_dataset_without_login(test_client_without_login):
    """
    Prueba que verifica que no se pueden descargar datasets sin iniciar sesión
    """
    response = test_client_without_login.get("/dataset/download_all?format=UVL")
    assert response.status_code == 302
    assert "/login" in response.location


@pytest.fixture
def test_client_multiple(test_app):
    with test_app.test_client() as client:
        login(client, "test@example.com", "test1234")
        yield client
        logout(client)


def test_download_all_dataset_multiple_empty(test_client_multiple):
    """
    Prueba que verifica el comportamiento al intentar descargar múltiples datasets vacíos
    """
    try:
        # Crear varios datasets vacíos
        datasets = []
        for i in range(3):
            ds_metrics = DSMetrics(number_of_models="0", number_of_features="0")
            db.session.add(ds_metrics)
            db.session.commit()

            ds_meta_data = DSMetaData(
                deposition_id=1000 + i,
                title=f"Empty Dataset {i}",
                description=f"Empty dataset {i} for testing",
                publication_type=PublicationType.JOURNAL_ARTICLE,
                publication_doi=f"10.1234/empty.{i}.doi",
                dataset_doi=f"10.1234/empty.dataset.{i}.doi",
                tags=f"empty, test, dataset{i}",
                ds_metrics_id=ds_metrics.id
            )
            db.session.add(ds_meta_data)
            db.session.commit()

            dataset = DataSet(user_id=1, ds_meta_data_id=ds_meta_data.id)
            db.session.add(dataset)
            db.session.commit()
            datasets.append((dataset, ds_meta_data, ds_metrics))

        # Probar la descarga
        formats = ["UVL", "DIMACS", "SPLOT", "GLENCOE"]
        for format in formats:
            response = test_client_multiple.get(f"/dataset/download_all?format={format}")
            assert response.status_code == 200
            assert len(response.data) > 0
            assert b"all_datasets.zip" in response.headers['Content-Disposition'].encode()

    finally:
        # Limpiar todos los datasets creados
        for dataset, meta_data, metrics in datasets:
            db.session.delete(dataset)
            db.session.delete(meta_data)
            db.session.delete(metrics)
        db.session.commit()
