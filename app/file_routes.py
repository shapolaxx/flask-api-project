"""
Маршруты для работы с файлами через Object Storage
"""

import os
import uuid
from datetime import datetime
from flask import jsonify, request, send_file, current_app
from werkzeug.utils import secure_filename
from .storage import storage


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB


def allowed_file(filename):
    """Проверить разрешен ли тип файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    """Получить расширение файла"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def generate_unique_filename(filename):
    """Сгенерировать уникальное имя файла"""
    extension = get_file_extension(filename)
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{unique_id}.{extension}"


def upload_file():
    """Загрузить файл в Object Storage"""
    try:
        # Проверяем наличие файла в запросе
        if 'file' not in request.files:
            return jsonify({'error': 'Файл не найден в запросе'}), 400
        
        file = request.files['file']
        
        # Проверяем что файл выбран
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        # Проверяем тип файла
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Недопустимый тип файла',
                'allowed_extensions': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Проверяем размер файла
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': 'Файл слишком большой',
                'max_size_mb': MAX_FILE_SIZE // (1024 * 1024)
            }), 400
        
        # Генерируем безопасное имя файла
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        
        # Сохраняем временно на диск
        temp_path = f"/tmp/{unique_filename}"
        file.save(temp_path)
        
        try:
            # Загружаем в Object Storage
            metadata = {
                'original_name': original_filename,
                'upload_time': datetime.now().isoformat(),
                'file_size': str(file_size),
                'content_type': file.content_type or 'application/octet-stream'
            }
            
            success = storage.upload_file(
                temp_path, 
                unique_filename, 
                metadata=metadata
            )
            
            if success:
                # Получаем информацию о загруженном файле
                file_info = storage.get_file_info(unique_filename)
                
                # Создаем presigned URL для доступа
                download_url = storage.get_presigned_url(unique_filename, expiration=3600)
                
                response_data = {
                    'message': 'Файл успешно загружен',
                    'filename': unique_filename,
                    'original_name': original_filename,
                    'size': file_size,
                    'content_type': file.content_type,
                    'download_url': download_url
                }
                
                if file_info:
                    response_data['file_info'] = file_info
                
                return jsonify(response_data), 201
            else:
                return jsonify({'error': 'Ошибка загрузки файла в storage'}), 500
                
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка при загрузке файла: {e}")
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


def download_file(filename):
    """Скачать файл из Object Storage"""
    try:
        # Проверяем существование файла
        file_info = storage.get_file_info(filename)
        if not file_info:
            return jsonify({'error': 'Файл не найден'}), 404
        
        # Создаем presigned URL для скачивания
        download_url = storage.get_presigned_url(filename, expiration=300)  # 5 минут
        
        if download_url:
            return jsonify({
                'download_url': download_url,
                'file_info': file_info,
                'expires_in': 300
            })
        else:
            return jsonify({'error': 'Ошибка создания ссылки для скачивания'}), 500
    
    except Exception as e:
        current_app.logger.error(f"Ошибка при скачивании файла {filename}: {e}")
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


def delete_file(filename):
    """Удалить файл из Object Storage"""
    try:
        # Проверяем существование файла
        file_info = storage.get_file_info(filename)
        if not file_info:
            return jsonify({'error': 'Файл не найден'}), 404
        
        # Удаляем файл
        success = storage.delete_file(filename)
        
        if success:
            return jsonify({
                'message': 'Файл успешно удален',
                'filename': filename
            })
        else:
            return jsonify({'error': 'Ошибка удаления файла'}), 500
    
    except Exception as e:
        current_app.logger.error(f"Ошибка при удалении файла {filename}: {e}")
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


def list_files():
    """Получить список файлов"""
    try:
        # Получаем параметры из query string
        prefix = request.args.get('prefix', '')
        limit = min(int(request.args.get('limit', 100)), 1000)  # Максимум 1000
        
        # Получаем список файлов
        files = storage.list_files(prefix=prefix)
        
        # Ограничиваем количество результатов
        if limit > 0:
            files = files[:limit]
        
        # Добавляем presigned URLs для каждого файла
        for file_data in files:
            file_data['download_url'] = storage.get_presigned_url(
                file_data['name'], 
                expiration=1800  # 30 минут
            )
        
        return jsonify({
            'files': files,
            'count': len(files),
            'prefix': prefix
        })
    
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении списка файлов: {e}")
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


def get_file_info(filename):
    """Получить информацию о файле"""
    try:
        file_info = storage.get_file_info(filename)
        
        if file_info:
            # Добавляем presigned URL
            file_info['download_url'] = storage.get_presigned_url(
                filename, 
                expiration=1800  # 30 минут
            )
            
            return jsonify(file_info)
        else:
            return jsonify({'error': 'Файл не найден'}), 404
    
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении информации о файле {filename}: {e}")
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


def storage_health():
    """Проверить состояние Object Storage"""
    try:
        is_healthy = storage.health_check()
        
        if is_healthy:
            return jsonify({
                'status': 'healthy',
                'message': 'Object Storage доступен',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'message': 'Object Storage недоступен',
                'timestamp': datetime.now().isoformat()
            }), 503
    
    except Exception as e:
        current_app.logger.error(f"Ошибка при проверке здоровья storage: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Ошибка проверки состояния storage',
            'timestamp': datetime.now().isoformat()
        }), 500