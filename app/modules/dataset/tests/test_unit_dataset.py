import pytest
from app import db
from app.modules.conftest import login, logout
from app.modules.dataset.models import DataSet, DSMetrics, DSMetaData, PublicationType
from app.modules.featuremodel.models import FeatureModel
from app.modules.hubfile.models import Hubfile
from app.modules.featuremodel.models import FMMetaData
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app.modules.dataset.services import DataSetService, features_counter
import json
import os
from flask import url_for


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
            dataset_doi="10.1234/dataset",
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

        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

        user_test2 = User(email='user2@example.com', password='test1234')
        db.session.add(user_test2)
        db.session.commit()

        profile2 = UserProfile(user_id=1, name="Name", surname="Surname")
        db.session.add(profile2)
        db.session.commit()

        ds_metrics_test_unsync = DSMetrics(
            number_of_models="3",
            number_of_features="10"
        )
        ds_meta_data_test_unsync = DSMetaData(
            title="Unsynchronized Dataset Title",
            description="This is an unsynchronized dataset description.",
            publication_type=PublicationType.JOURNAL_ARTICLE,
            publication_doi="10.5678/unsync.doi",
            tags="unsync, dataset, example",
            ds_metrics=ds_metrics_test_unsync
        )
        db.session.add_all([ds_metrics_test_unsync, ds_meta_data_test_unsync])

        dataset_test_unsync = DataSet(
            user_id=2,
            ds_meta_data_id=2
        )
        db.session.add(dataset_test_unsync)

        feature_model_meta_data_unsync = FMMetaData(
            uvl_filename="unsync_file.uvl",
            title="Unsynchronized Feature Model",
            description="This is an unsynchronized feature model description.",
            publication_type=PublicationType.JOURNAL_ARTICLE,
            publication_doi="10.5678/unsync.doi",
            tags="unsync, feature, model",
            uvl_version="1.0"
        )
        db.session.add(feature_model_meta_data_unsync)
        db.session.commit()

        feature_model_test_unsync = FeatureModel(
            data_set_id=2,
            fm_meta_data_id=1
        )
        db.session.add(feature_model_test_unsync)
        db.session.commit()

        hubfile1_unsync = Hubfile(
            name="unsync_file1.uvl",
            checksum="xyz123",
            size=512,
            feature_model_id=2
        )
        hubfile2_unsync = Hubfile(
            name="unsync_file2.uvl",
            checksum="uvw456",
            size=1024,
            feature_model_id=2
        )
        db.session.add_all([hubfile1_unsync, hubfile2_unsync])
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
    user_id = 3

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


# Tests unitarios relaccionados con Fakenodo (Issue #5)
def test_simple_hierarchy():
    """
    Verifica que funciona y que coincide con la salida esperada
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)

    # Archivo con una jerarquía básica
    content = """features
    Chat
        mandatory
            Connection
                alternative
                    "Peer 2 Peer"
                    Server
            Messages
                or
                    Text
                    Video
                    Audio
        optional
            "Data Storage"
            "Media Player"
"""
    # Crear un archivo temporal con el contenido proporcionado
    file_path = os.path.join(temp_dir, "simple.uvl")
    with open(file_path, 'w') as f:
        f.write(content)

    # Llamar al método parse_uvl_to_json
    result = DataSetService.parse_uvl_to_json(file_path)
    result_json = json.loads(result)

    # Verificar el resultado
    expected_output = {
        "features": {
            "Chat": {
                "mandatory": {
                    "Connection": {
                        "alternative": {
                            '"Peer 2 Peer"': {},
                            "Server": {}
                        }
                    },
                    "Messages": {
                        "or": {
                            "Text": {},
                            "Video": {},
                            "Audio": {}
                        }
                    }
                },
                "optional": {
                    '"Data Storage"': {},
                    '"Media Player"': {}
                }
            }
        }
    }
    assert result_json == expected_output

    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)


def test_empty_file():
    """
    Verifica que no hay fallos o errores cuando recibe un fichero vacío
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)
    # Archivo vacío
    file_path = os.path.join(temp_dir, "empty.uvl")
    with open(file_path, 'w') as f:
        f.write("")

    # Llamar al método parse_uvl_to_json
    result = DataSetService.parse_uvl_to_json(file_path)
    result_json = json.loads(result)

    # Verificar que el resultado sea un diccionario vacío
    assert result_json == {}

    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)


def test_single_level():
    """
    Verifica que funciona cuando hay una sola línea sin jerarquía
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)

    # Archivo con una sola línea sin jerarquía
    content = "features"
    file_path = os.path.join(temp_dir, "single_level.uvl")
    with open(file_path, 'w') as f:
        f.write(content)

    # Llamar al método parse_uvl_to_json
    result = DataSetService.parse_uvl_to_json(file_path)
    result_json = json.loads(result)

    # Verificar el resultado
    expected_output = {"features": {}}
    assert result_json == expected_output

    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)


def test_inconsistent_indentation():
    """
    Verifica que funciona aunque tenga indentaciones inconsistentes
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)

    # Archivo con indentación inconsistente
    content = """features
    Chat
                mandatory
                        Connection"""
    file_path = os.path.join(temp_dir, "inconsistent.uvl")
    with open(file_path, 'w') as f:
        f.write(content)

    # Llamar al método parse_uvl_to_json
    result = DataSetService.parse_uvl_to_json(file_path)
    result_json = json.loads(result)

    # Verificar el resultado
    expected_output = {
        "features": {
            "Chat": {
                "mandatory": {
                    "Connection": {}
                }
            }
        }
    }
    assert result_json == expected_output

    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)


def test_complex_hierarchy():
    """
    Verifica que funciona correctamente incluso cuando la jerarquía es compleja
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)

    # Archivo con una jerarquía más compleja
    content = """root
    level1
        level2a
            level3a
                level4a
                level4b
            level3b
                level4a
                level4b
            level3c
        level2b
    level1b"""
    file_path = os.path.join(temp_dir, "complex.uvl")
    with open(file_path, 'w') as f:
        f.write(content)

    # Llamar al método parse_uvl_to_json
    result = DataSetService.parse_uvl_to_json(file_path)
    result_json = json.loads(result)

    # Verificar el resultado
    expected_output = {
        "root": {
            "level1": {
                "level2a": {
                    "level3a": {
                        "level4a": {},
                        "level4b": {}
                    },
                    "level3b": {
                        "level4a": {},
                        "level4b": {}
                    },
                    "level3c": {}
                },
                "level2b": {}
            },
            "level1b": {}
        }
    }
    assert result_json == expected_output

    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)


# Tests unitarios relaccionados con Explore (Issue #6)
def test_basic_feature_count():
    """
    Verifica que el método cuenta correctamente las features básicas dentro del bloque "features"
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)

    content = """features
    Chat
    Video
    Audio"""
    file_path = os.path.join(temp_dir, "basic.uvl")
    with open(file_path, 'w') as f:
        f.write(content)

    # Llamar al método
    result = features_counter(file_path)

    # Verificar el resultado
    assert result == 3

    # Limpieza
    os.remove(file_path)
    os.rmdir(temp_dir)


def test_no_features_block():
    """
    Verifica que devuelve 0 cuando no hay un bloque "features" en el archivo
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)

    content = """Chat
    Video
    Audio"""
    file_path = os.path.join(temp_dir, "no_features.uvl")
    with open(file_path, 'w') as f:
        f.write(content)

    # Llamar al método
    result = features_counter(file_path)

    # Verificar el resultado
    assert result == 0

    # Limpieza
    os.remove(file_path)
    os.rmdir(temp_dir)


def test_nested_features():
    """
    Verifica que cuenta correctamente las features incluso si están anidadas
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)

    content = """features
    Chat
        mandatory
            Video
            Audio"""
    file_path = os.path.join(temp_dir, "nested.uvl")
    with open(file_path, 'w') as f:
        f.write(content)

    # Llamar al método
    result = features_counter(file_path)

    # Verificar el resultado
    assert result == 3

    # Limpieza
    os.remove(file_path)
    os.rmdir(temp_dir)


def test_empty_features_block():
    """
    Verifica que devuelve 0 cuando el bloque "features" está vacío
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)

    content = """features"""
    file_path = os.path.join(temp_dir, "empty_features.uvl")
    with open(file_path, 'w') as f:
        f.write(content)

    # Llamar al método
    result = features_counter(file_path)

    # Verificar el resultado
    assert result == 0

    # Limpieza
    os.remove(file_path)
    os.rmdir(temp_dir)


def test_features_with_keywords():
    """
    Verifica que no cuenta las palabras clave como features dentro del bloque "features"
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)

    content = """features
    Chat
    mandatory
    or
    Video"""
    file_path = os.path.join(temp_dir, "with_keywords.uvl")
    with open(file_path, 'w') as f:
        f.write(content)

    # Llamar al método
    result = features_counter(file_path)

    # Verificar el resultado
    assert result == 2  # Solo cuenta "Chat" y "Video"

    # Limpieza
    os.remove(file_path)
    os.rmdir(temp_dir)


def test_features_block_with_exit():
    """
    Verifica que el conteo se detiene al salir del bloque "features"
    """
    temp_dir = "temp_test_files"
    os.makedirs(temp_dir, exist_ok=True)

    content = """features
    Chat
    Video
    Audio
OtherSection
    NotFeature"""
    file_path = os.path.join(temp_dir, "exit_block.uvl")
    with open(file_path, 'w') as f:
        f.write(content)

    # Llamar al método
    result = features_counter(file_path)

    # Verificar el resultado
    assert result == 3  # Solo cuenta hasta "Audio"

    # Limpieza
    os.remove(file_path)


# Tests unitarios relaccionados con Staging Area (Issue #7)
def test_create_dataset_draft_missing_title(test_client):

    login(test_client, "user@example.com", "test1234")
    # Form sin archivo y sin titulo
    form_data = {
        'title': '',
        'description': 'Test Description',
        'publication_type': 'JOURNAL_ARTICLE',
        'publication_doi': '10.1234/test.doi',
        'dataset_doi': '10.1234/dataset.doi',
        'tags': 'test, dataset, example'
    }
    response = test_client.post(url_for('dataset.create_dataset_draft'), data=form_data)
    logout(test_client)
    assert response.status_code == 400

    # Verifica que le falta el titulo
    assert "This field is required." in response.json["message"]["title"]


def test_create_dataset_draft_post_exception(test_client):

    login(test_client, "user@example.com", "test1234")

    # Form sin archivo
    form_data = {
        'title': 'Test Dataset',
        'description': 'Test Description',
        'publication_type': 'JOURNAL_ARTICLE',
        'publication_doi': '10.1234/test.doi',
        'dataset_doi': '10.1234/dataset.doi',
        'tags': 'test, dataset, example'
    }
    response = test_client.post(url_for('dataset.create_dataset_draft'), data=form_data)
    logout(test_client)

    # Verifica que no se ha subido ningún archivo
    assert response.status_code == 400


def test_get_draft_dataset(test_client):

    login(test_client, "user@example.com", "test1234")

    # Get de un dataset en stagin area
    response = test_client.get('/dataset/unsynchronized/2/')

    logout(test_client)

    assert response.status_code == 200


def test_no_login_edit_draft(test_client):

    login(test_client, "user@example.com", "test1234")
    logout(test_client)
    # Get edit page without login
    response = test_client.get('dataset/edit/2')

    assert response.status_code == 302


def test_edit_other_user_draft(test_client):
    form_data = {
        'title': 'title',
        'desc': 'Test Description',
        'publication_type': PublicationType.JOURNAL_ARTICLE.value,
        'publication_doi': 'https://prueba.com',
        'tags': 'test, dataset, example'
    }

    login(test_client, "user2@example.com", "test1234")

    response = test_client.post('dataset/edit/2', data=form_data)

    logout(test_client)

    assert response.status_code == 400


def test_edit_published_dataset(test_client):

    login(test_client, "user2@example.com", "test1234")

    response = test_client.post('dataset/edit/1')

    logout(test_client)

    assert response.status_code == 400


def test_edit_draft_empty_title(test_client):
    form_data = {
        'title': None,
        'desc': 'Test Description',
        'publication_type': PublicationType.JOURNAL_ARTICLE.value,
        'publication_doi': 'https://prueba.com',
        'tags': 'test, dataset, example'
    }
    login(test_client, "user@example.com", "test1234")

    response = test_client.post('dataset/edit/2', data=form_data)
    logout(test_client)
    assert response.request.path == url_for("dataset.edit_dataset", dataset_id=2)


def test_edit_draft_empty_description(test_client):
    form_data = {
        'title': 'Test Dataset',
        'desc': '',
        'publication_type': PublicationType.JOURNAL_ARTICLE.value,
        'publication_doi': 'http://prueba.com',
        'tags': 'test, dataset, example'
    }
    login(test_client, "user@example.com", "test1234")

    response = test_client.post('dataset/edit/2', data=form_data, follow_redirects=True)
    logout(test_client)
    assert response.request.path == url_for("dataset.edit_dataset", dataset_id=2)


def test_edit_draft_bad_doi(test_client):
    form_data = {
        'title': 'Test Dataset',
        'desc': 'Test Description',
        'publication_type': PublicationType.JOURNAL_ARTICLE.value,
        'publication_doi': 'hola',
        'tags': 'test, dataset, example'
    }
    login(test_client, "user@example.com", "test1234")

    response = test_client.post('dataset/edit/2', data=form_data, follow_redirects=True)
    logout(test_client)
    assert response.request.path == url_for("dataset.edit_dataset", dataset_id=2)


def test_edit_draft(test_client):
    form_data = {
        'title': 'title',
        'desc': 'Test Description',
        'publication_type': PublicationType.JOURNAL_ARTICLE.value,
        'publication_doi': 'https://prueba.com',
        'tags': 'test, dataset, example'
    }

    login(test_client, "user@example.com", "test1234")

    response = test_client.post('dataset/edit/2', data=form_data, follow_redirects=True)

    logout(test_client)

    assert response.status_code == 200


def test_get_edit_draft(test_client):

    login(test_client, "user@example.com", "test1234")

    response = test_client.get('/dataset/edit/2')
    logout(test_client)
    assert response.status_code == 200


def test_publish_draft_dataset_no_login(test_client):

    # Publicar sin iniciar sesión
    response = test_client.get('/dataset/publish/2')
    assert response.status_code == 302

    response = test_client.get('/doi/10.1234/dataset2', follow_redirects=True)
    assert response.status_code == 404


def test_publish_draft_dataset_other_user(test_client):

    login(test_client, "user2@example.com", "test1234")

    # Publicar un dataset de otro usuario
    response = test_client.get('/dataset/publish/2')
    assert response.status_code == 400

    response = test_client.get('/doi/10.1234/dataset2', follow_redirects=True)
    logout(test_client)
    assert response.status_code == 404


def test_already_published_dataset(test_client):

    login(test_client, "user2@example.com", "test1234")

    # Publicar un dataset que ya está publicado
    response = test_client.get('/dataset/publish/1')
    assert response.status_code == 400

    response = test_client.get('/doi/10.1234/dataset1', follow_redirects=True)
    logout(test_client)
    assert response.status_code == 404


def test_publish_draft_dataset(test_client):

    # Archivo necesario para la publicación del dataset
    os.makedirs('uploads/user_2/dataset_2', exist_ok=True)
    content = """features
    Chat
        mandatory
            Connection
                alternative
                    "Peer 2 Peer"
                    Server
            Messages
                or
                    Text
                    Video
                    Audio
        optional
            "Data Storage"
            "Media Player"
"""
    with open('uploads/user_2/dataset_2/unsync_file.uvl', 'w') as f:
        f.write(content)

    login(test_client, "user@example.com", "test1234")

    # Publicar un dataset en staging area
    response = test_client.get('/dataset/publish/2')
    assert response.status_code == 200

    # Verifica que se ha publicado
    response = test_client.get('/doi/10.1234/dataset2', follow_redirects=True)
    logout(test_client)
    assert response.status_code == 200
