"""
Модуль для работы с Object Storage (S3/MinIO)
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from minio import Minio
from minio.error import S3Error
from flask import current_app


logger = logging.getLogger(__name__)


class StorageConfig:
    """Конфигурация для Object Storage"""
    
    def __init__(self):
        self.endpoint = os.getenv('STORAGE_ENDPOINT', 'localhost:9000')
        self.access_key = os.getenv('STORAGE_ACCESS_KEY', 'minioadmin')
        self.secret_key = os.getenv('STORAGE_SECRET_KEY', 'minioadmin')
        self.bucket_name = os.getenv('STORAGE_BUCKET', 'flask-api-bucket')
        self.secure = os.getenv('STORAGE_SECURE', 'false').lower() == 'true'
        self.region = os.getenv('STORAGE_REGION', 'us-east-1')
        
        # Для AWS S3
        self.use_aws = os.getenv('USE_AWS_S3', 'false').lower() == 'true'


class ObjectStorage:
    """Универсальный класс для работы с Object Storage"""
    
    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig()
        self._client = None
        self._minio_client = None
        
    def _get_boto3_client(self):
        """Получить boto3 клиент для AWS S3"""
        if self._client is None:
            try:
                if self.config.use_aws:
                    # Для AWS S3
                    self._client = boto3.client(
                        's3',
                        region_name=self.config.region
                    )
                else:
                    # Для S3-совместимого storage (MinIO)
                    self._client = boto3.client(
                        's3',
                        endpoint_url=f"{'https' if self.config.secure else 'http'}://{self.config.endpoint}",
                        aws_access_key_id=self.config.access_key,
                        aws_secret_access_key=self.config.secret_key,
                        region_name=self.config.region
                    )
                logger.info("Boto3 клиент инициализирован")
            except Exception as e:
                logger.error(f"Ошибка инициализации boto3 клиента: {e}")
                raise
        return self._client
    
    def _get_minio_client(self):
        """Получить MinIO клиент"""
        if self._minio_client is None:
            try:
                self._minio_client = Minio(
                    self.config.endpoint,
                    access_key=self.config.access_key,
                    secret_key=self.config.secret_key,
                    secure=self.config.secure
                )
                logger.info("MinIO клиент инициализирован")
            except Exception as e:
                logger.error(f"Ошибка инициализации MinIO клиента: {e}")
                raise
        return self._minio_client
    
    def ensure_bucket_exists(self) -> bool:
        """Убедиться что bucket существует, создать если нет"""
        try:
            client = self._get_minio_client()
            
            if not client.bucket_exists(self.config.bucket_name):
                client.make_bucket(self.config.bucket_name)
                logger.info(f"Bucket '{self.config.bucket_name}' создан")
            else:
                logger.info(f"Bucket '{self.config.bucket_name}' уже существует")
            
            return True
        except S3Error as e:
            logger.error(f"Ошибка при работе с bucket: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при создании bucket: {e}")
            return False
    
    def upload_file(self, file_path: str, object_name: Optional[str] = None, 
                   metadata: Optional[Dict[str, str]] = None) -> bool:
        """
        Загрузить файл в Object Storage
        
        Args:
            file_path: Путь к файлу для загрузки
            object_name: Имя объекта в storage (если None, используется имя файла)
            metadata: Дополнительные метаданные
            
        Returns:
            True если загрузка успешна, False иначе
        """
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return False
        
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        try:
            client = self._get_boto3_client()
            
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            client.upload_file(
                file_path, 
                self.config.bucket_name, 
                object_name,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Файл успешно загружен: {object_name}")
            return True
            
        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            return False
        except NoCredentialsError:
            logger.error("Учетные данные не найдены")
            return False
        except ClientError as e:
            logger.error(f"Ошибка клиента при загрузке: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке: {e}")
            return False
    
    def download_file(self, object_name: str, file_path: str) -> bool:
        """
        Скачать файл из Object Storage
        
        Args:
            object_name: Имя объекта в storage
            file_path: Путь для сохранения файла
            
        Returns:
            True если скачивание успешно, False иначе
        """
        try:
            client = self._get_boto3_client()
            client.download_file(self.config.bucket_name, object_name, file_path)
            
            logger.info(f"Файл успешно скачан: {object_name} -> {file_path}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.error(f"Объект не найден: {object_name}")
            else:
                logger.error(f"Ошибка клиента при скачивании: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при скачивании: {e}")
            return False
    
    def delete_file(self, object_name: str) -> bool:
        """
        Удалить файл из Object Storage
        
        Args:
            object_name: Имя объекта для удаления
            
        Returns:
            True если удаление успешно, False иначе
        """
        try:
            client = self._get_boto3_client()
            client.delete_object(Bucket=self.config.bucket_name, Key=object_name)
            
            logger.info(f"Объект успешно удален: {object_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Ошибка клиента при удалении: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при удалении: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """
        Получить список файлов в bucket
        
        Args:
            prefix: Префикс для фильтрации объектов
            
        Returns:
            Список словарей с информацией о файлах
        """
        try:
            client = self._get_boto3_client()
            
            kwargs = {'Bucket': self.config.bucket_name}
            if prefix:
                kwargs['Prefix'] = prefix
            
            response = client.list_objects_v2(**kwargs)
            
            if 'Contents' not in response:
                return []
            
            files = []
            for obj in response['Contents']:
                files.append({
                    'name': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag'].strip('"')
                })
            
            logger.info(f"Найдено {len(files)} объектов с префиксом '{prefix}'")
            return files
            
        except ClientError as e:
            logger.error(f"Ошибка клиента при получении списка: {e}")
            return []
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении списка: {e}")
            return []
    
    def get_presigned_url(self, object_name: str, expiration: int = 3600) -> Optional[str]:
        """
        Получить подписанный URL для доступа к объекту
        
        Args:
            object_name: Имя объекта
            expiration: Время жизни URL в секундах (по умолчанию 1 час)
            
        Returns:
            Подписанный URL или None при ошибке
        """
        try:
            client = self._get_boto3_client()
            
            response = client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.config.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            
            logger.info(f"Создан presigned URL для {object_name}")
            return response
            
        except ClientError as e:
            logger.error(f"Ошибка при создании presigned URL: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при создании presigned URL: {e}")
            return None
    
    def get_file_info(self, object_name: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о файле
        
        Args:
            object_name: Имя объекта
            
        Returns:
            Словарь с информацией о файле или None при ошибке
        """
        try:
            client = self._get_boto3_client()
            
            response = client.head_object(
                Bucket=self.config.bucket_name, 
                Key=object_name
            )
            
            return {
                'name': object_name,
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response.get('ContentType', 'unknown'),
                'etag': response['ETag'].strip('"'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Объект не найден: {object_name}")
            else:
                logger.error(f"Ошибка при получении информации о файле: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении информации о файле: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Проверка доступности Object Storage
        
        Returns:
            True если storage доступен, False иначе
        """
        try:
            client = self._get_boto3_client()
            client.list_buckets()
            logger.info("Object Storage доступен")
            return True
        except Exception as e:
            logger.error(f"Object Storage недоступен: {e}")
            return False


# Глобальный экземпляр для использования в приложении
storage = ObjectStorage()


def init_storage(app):
    """Инициализация Object Storage для Flask приложения"""
    # Проверяем нужно ли пропустить инициализацию storage
    if os.getenv('SKIP_STORAGE_INIT', 'false').lower() == 'true':
        app.logger.info("Инициализация Object Storage пропущена")
        return
    
    try:
        # Проверяем доступность storage
        if storage.health_check():
            # Создаем bucket если его нет
            storage.ensure_bucket_exists()
            app.logger.info("Object Storage успешно инициализирован")
        else:
            app.logger.warning("Object Storage недоступен")
    except Exception as e:
        app.logger.error(f"Ошибка инициализации Object Storage: {e}")