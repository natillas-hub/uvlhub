import pytest
from app import db
from app.modules.dataset.models import DataSet, DSMetrics, DSMetaData, PublicationType, Author
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from datetime import datetime, timezone


@pytest.fixture(scope="module")
def test_client(test_client):
    """Fixture que prepara datos de prueba para integración"""
    with test_client.application.app_context():
        # Crear autor del dataset
        author = Author(
            name="Test Author",
            affiliation="Test University",
            orcid="0000-0000-0000-0000"
        )
        db.session.add(author)

        # Crear dataset siguiendo la estructura del seeder
        ds_metrics = DSMetrics(
            number_of_models="5",
            number_of_features="20"
        )

        ds_meta_data = DSMetaData(
            deposition_id=123456,
            title="Test Integration Dataset",
            description="Dataset for integration testing",
            publication_type=PublicationType.JOURNAL_ARTICLE,
            publication_doi="10.1234/test.integration",
            dataset_doi="10.5678/dataset.integration",
            tags="test, integration",
            ds_metrics=ds_metrics,
            authors=[author]
        )

        dataset = DataSet(
            user_id=1,
            ds_meta_data=ds_meta_data,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(dataset)

        # Crear feature model siguiendo la estructura del seeder
        fm_meta_data = FMMetaData(
            uvl_filename="test_model.uvl",
            title="Test Feature Model",
            description="Feature model for testing",
            publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
            publication_doi="10.1234/fm.test",
            tags="test, features",
            uvl_version="1.0"
        )

        feature_model = FeatureModel(
            data_set=dataset,
            fm_meta_data=fm_meta_data
        )
        db.session.add(feature_model)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear datos de prueba: {str(e)}")
            raise e

    yield test_client


def test_explore_integration_full_search(test_client):
    """Test integración de búsqueda completa"""
    response = test_client.post(
        '/explore',
        json={
            'query': 'Test Integration',
            'publication_type': 'article',
            'sorting': 'newest',
            'min_features': 10,
            'max_features': 30
        })
    assert response.status_code == 200
    data = response.json
    assert len(data) > 0
    assert 'Test Integration Dataset' in data[0]['title']


def test_explore_integration_author_search(test_client):
    """Test integración de búsqueda por autor"""
    response = test_client.post(
        '/explore',
        json={
            'query': 'Test Author',
            'publication_type': 'any',
            'sorting': 'newest'
        })
    assert response.status_code == 200
    data = response.json
    assert len(data) > 0
    assert any('Test Author' in str(dataset['authors']) for dataset in data)
