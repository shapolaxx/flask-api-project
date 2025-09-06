"""
Тесты для функциональности Object Storage
"""

import pytest
import os
from unittest.mock import Mock, patch
from app import create_app
from app.storage import ObjectStorage, StorageConfig


@pytest.fixture
def app():
    """Создать тестовое приложение"""
    # Настроим окружение для тестирования
    os.environ['SKIP_STORAGE_INIT'] = 'true'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app()
    app.config['TESTING'] = True
    
    yield app
    
    # Очистка
    if 'SKIP_STORAGE_INIT' in os.environ:
        del os.environ['SKIP_STORAGE_INIT']


@pytest.fixture
def client(app):
    """Создать тестовый клиент"""
    return app.test_client()


class TestStorageConfig:
    """Тесты конфигурации storage"""
    
    def test_default_config(self):
        """Тест конфигурации по умолчанию"""
        config = StorageConfig()
        
        assert config.endpoint == 'localhost:9000'
        assert config.access_key == 'minioadmin'
        assert config.secret_key == 'minioadmin'
        assert config.bucket_name == 'flask-api-bucket'
        assert config.secure == False
        assert config.use_aws == False
    
    def test_env_config(self):
        """Тест конфигурации из переменных окружения"""
        with patch.dict(os.environ, {
            'STORAGE_ENDPOINT': 'test.example.com:9000',
            'STORAGE_ACCESS_KEY': 'test_access',
            'STORAGE_SECRET_KEY': 'test_secret',
            'STORAGE_BUCKET': 'test-bucket',
            'STORAGE_SECURE': 'true',
            'USE_AWS_S3': 'true'
        }):
            config = StorageConfig()
            
            assert config.endpoint == 'test.example.com:9000'
            assert config.access_key == 'test_access'
            assert config.secret_key == 'test_secret'
            assert config.bucket_name == 'test-bucket'
            assert config.secure == True
            assert config.use_aws == True


class TestStorageEndpoints:
    """Тесты API эндпоинтов для работы с файлами"""
    
    def test_list_files_empty(self, client):
        """Тест получения пустого списка файлов"""
        with patch('app.file_routes.storage.list_files', return_value=[]):
            response = client.get('/files')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] == 0
            assert data['files'] == []
    
    def test_list_files_with_data(self, client):
        """Тест получения списка файлов с данными"""
        mock_files = [
            {
                'name': 'test1.txt',
                'size': 100,
                'last_modified': '2025-01-01T00:00:00Z',
                'etag': 'abc123'
            },
            {
                'name': 'test2.jpg',
                'size': 2048,
                'last_modified': '2025-01-02T00:00:00Z',
                'etag': 'def456'
            }
        ]
        
        with patch('app.file_routes.storage.list_files', return_value=mock_files):
            with patch('app.file_routes.storage.get_presigned_url', return_value='http://example.com/download'):
                response = client.get('/files')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['count'] == 2
                assert len(data['files']) == 2
                assert data['files'][0]['name'] == 'test1.txt'
                assert 'download_url' in data['files'][0]
    
    def test_list_files_with_prefix(self, client):
        """Тест получения файлов с префиксом"""
        with patch('app.file_routes.storage.list_files', return_value=[]) as mock_list:
            response = client.get('/files?prefix=images/')
            
            assert response.status_code == 200
            mock_list.assert_called_once_with(prefix='images/')
    
    def test_get_file_info_existing(self, client):
        """Тест получения информации о существующем файле"""
        mock_info = {
            'name': 'test.txt',
            'size': 100,
            'content_type': 'text/plain',
            'last_modified': '2025-01-01T00:00:00Z'
        }
        
        with patch('app.file_routes.storage.get_file_info', return_value=mock_info):
            with patch('app.file_routes.storage.get_presigned_url', return_value='http://example.com/download'):
                response = client.get('/files/test.txt/info')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['name'] == 'test.txt'
                assert data['size'] == 100
                assert 'download_url' in data
    
    def test_get_file_info_not_found(self, client):
        """Тест получения информации о несуществующем файле"""
        with patch('app.file_routes.storage.get_file_info', return_value=None):
            response = client.get('/files/nonexistent.txt/info')
            
            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data
    
    def test_download_file_existing(self, client):
        """Тест скачивания существующего файла"""
        mock_info = {'name': 'test.txt', 'size': 100}
        
        with patch('app.file_routes.storage.get_file_info', return_value=mock_info):
            with patch('app.file_routes.storage.get_presigned_url', return_value='http://example.com/download'):
                response = client.get('/files/test.txt/download')
                
                assert response.status_code == 200
                data = response.get_json()
                assert 'download_url' in data
                assert 'file_info' in data
                assert data['expires_in'] == 300
    
    def test_download_file_not_found(self, client):
        """Тест скачивания несуществующего файла"""
        with patch('app.file_routes.storage.get_file_info', return_value=None):
            response = client.get('/files/nonexistent.txt/download')
            
            assert response.status_code == 404
    
    def test_delete_file_existing(self, client):
        """Тест удаления существующего файла"""
        mock_info = {'name': 'test.txt', 'size': 100}
        
        with patch('app.file_routes.storage.get_file_info', return_value=mock_info):
            with patch('app.file_routes.storage.delete_file', return_value=True):
                response = client.delete('/files/test.txt')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['message'] == 'Файл успешно удален'
                assert data['filename'] == 'test.txt'
    
    def test_delete_file_not_found(self, client):
        """Тест удаления несуществующего файла"""
        with patch('app.file_routes.storage.get_file_info', return_value=None):
            response = client.delete('/files/nonexistent.txt')
            
            assert response.status_code == 404
    
    def test_storage_health_healthy(self, client):
        """Тест health check когда storage доступен"""
        with patch('app.file_routes.storage.health_check', return_value=True):
            response = client.get('/health/storage')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
    
    def test_storage_health_unhealthy(self, client):
        """Тест health check когда storage недоступен"""
        with patch('app.file_routes.storage.health_check', return_value=False):
            response = client.get('/health/storage')
            
            assert response.status_code == 503
            data = response.get_json()
            assert data['status'] == 'unhealthy'
    
    def test_upload_file_no_file(self, client):
        """Тест загрузки без файла"""
        response = client.post('/files/upload')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_upload_file_empty_filename(self, client):
        """Тест загрузки с пустым именем файла"""
        response = client.post('/files/upload', data={'file': (None, '')})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestObjectStorage:
    """Тесты класса ObjectStorage"""
    
    def test_init_with_config(self):
        """Тест инициализации с конфигурацией"""
        config = StorageConfig()
        storage = ObjectStorage(config)
        
        assert storage.config == config
    
    def test_init_without_config(self):
        """Тест инициализации без конфигурации"""
        storage = ObjectStorage()
        
        assert isinstance(storage.config, StorageConfig)
    
    @patch('app.storage.boto3.client')
    def test_get_boto3_client(self, mock_boto3):
        """Тест получения boto3 клиента"""
        storage = ObjectStorage()
        client = storage._get_boto3_client()
        
        mock_boto3.assert_called_once()
        assert client == mock_boto3.return_value
    
    @patch('app.storage.Minio')
    def test_get_minio_client(self, mock_minio):
        """Тест получения MinIO клиента"""
        storage = ObjectStorage()
        client = storage._get_minio_client()
        
        mock_minio.assert_called_once()
        assert client == mock_minio.return_value