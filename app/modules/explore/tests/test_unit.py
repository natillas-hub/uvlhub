import pytest
from flask import url_for

# Test de GET /explore
def test_explore_get(test_client):
    """Test que la ruta /explore responde correctamente con GET"""
    response = test_client.get('/explore')
    assert response.status_code == 200
    assert b'Explore' in response.data

# Test POST sin filtros
def test_explore_post_empty(test_client):
    """Test búsqueda sin criterios"""
    response = test_client.post('/explore', 
                              json={
                                  'query': '',
                                  'publication_type': 'any',
                                  'sorting': 'newest',
                                  'min_features': None,
                                  'max_features': None,
                                  'min_products': None,
                                  'max_products': None
                              })
    assert response.status_code == 200
    assert isinstance(response.json, list)
#
#  TEst con query de busqueada
def test_explore_post_with_query(test_client):
    """Test búsqueda con query"""
    response = test_client.post('/explore',
                              json={
                                  'query': 'test',
                                  'publication_type': 'any',
                                  'sorting': 'newest'
                              })
    assert response.status_code == 200
    assert isinstance(response.json, list)

#Test con tipo de publicacion
def test_explore_post_with_publication_type(test_client):
    """Test filtrado por tipo de publicación"""
    response = test_client.post('/explore',
                              json={
                                  'query': '',
                                  'publication_type': 'article',
                                  'sorting': 'newest'
                              })
    assert response.status_code == 200
    assert isinstance(response.json, list)

# Test con diferentes ordenamientos
def test_explore_post_with_sorting(test_client):
    """Test ordenamiento"""
    # Test ordenamiento más nuevo primero
    response_newest = test_client.post('/explore',
                                     json={
                                         'query': '',
                                         'publication_type': 'any',
                                         'sorting': 'newest'
                                     })
    assert response_newest.status_code == 200
    
    # Test ordenamiento más antiguo primero
    response_oldest = test_client.post('/explore',
                                     json={
                                         'query': '',
                                         'publication_type': 'any',
                                         'sorting': 'oldest'
                                     })
    assert response_oldest.status_code == 200

# Test con limites de features
def test_explore_post_with_feature_limits(test_client):
    """Test filtrado por número de features"""
    response = test_client.post('/explore',
                              json={
                                  'query': '',
                                  'publication_type': 'any',
                                  'sorting': 'newest',
                                  'min_features': 1,
                                  'max_features': 100
                              })
    assert response.status_code == 200
    assert isinstance(response.json, list)

# Test con limites de productos
def test_explore_post_with_product_limits(test_client):
    """Test filtrado por número de productos"""
    response = test_client.post('/explore',
                              json={
                                  'query': '',
                                  'publication_type': 'any',
                                  'sorting': 'newest',
                                  'min_products': 1,
                                  'max_products': 100
                              })
    assert response.status_code == 200
    assert isinstance(response.json, list)

# Test con tipo de publicación inválido
def test_explore_with_invalid_publication_type(test_client):
    """Test con tipo de publicación inválido"""
    response = test_client.post('/explore',
                              json={
                                  'query': '',
                                  'publication_type': 'invalid_type',
                                  'sorting': 'newest'
                              })
    assert response.status_code == 200
    assert isinstance(response.json, list)

# Test con un valor de ordenamiento inválido
def test_explore_post_invalid_sorting(test_client):
    """Test con un valor de ordenamiento inválido"""
    response = test_client.post('/explore',
                              json={
                                  'query': '',
                                  'publication_type': 'any',
                                  'sorting': 'invalid_sort'  # Valor inválido
                              })
    assert response.status_code == 200  # Debería usar el valor por defecto 'newest'
    assert isinstance(response.json, list)

# Test con valores negativos para features
def test_explore_post_negative_features(test_client):
    """Test con valores negativos para features"""
    response = test_client.post('/explore',
                              json={
                                  'query': '',
                                  'publication_type': 'any',
                                  'sorting': 'newest',
                                  'min_features': -1,  # Valor inválido
                                  'max_features': -5   # Valor inválido
                              })
    assert response.status_code == 400
    assert 'error' in response.json

# Test con rango inválido de features (min > max)
def test_explore_post_invalid_feature_range(test_client):
    """Test con rango inválido de features (min > max)"""
    response = test_client.post('/explore',
                              json={
                                  'query': '',
                                  'publication_type': 'any',
                                  'sorting': 'newest',
                                  'min_features': 100,
                                  'max_features': 50
                              })
    assert response.status_code == 400
    assert 'error' in response.json

# Test con rango inválido de productos (min > max)
def test_explore_post_invalid_product_range(test_client):
    """Test con rango inválido de productos (min > max)"""
    response = test_client.post('/explore',
                              json={
                                  'query': '',
                                  'publication_type': 'any',
                                  'sorting': 'newest',
                                  'min_products': 1000,
                                  'max_products': 500
                              })
    assert response.status_code == 400
    assert 'error' in response.json

# Test con JSON mal formado
def test_explore_post_malformed_json(test_client):
    """Test con JSON mal formado"""
    response = test_client.post('/explore',
                              data='invalid json',
                              content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.json

# Test con campos requeridos faltantes
def test_explore_post_missing_required_fields(test_client):
    """Test con campos requeridos faltantes"""
    response = test_client.post('/explore',
                              json={
                                  # Falta el campo 'sorting'
                                  'query': '',
                                  'publication_type': 'any'
                              })
    assert response.status_code == 400
    assert 'error' in response.json 