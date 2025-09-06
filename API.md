# 📡 API Документация

Подробная документация API для Flask приложения с тестовой инфраструктурой.

## 🔗 Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://your-domain.com`

## 🔐 Аутентификация

В текущей версии аутентификация не требуется. В будущих версиях планируется добавление JWT токенов.

## 📋 Основные Endpoints

### 1. Health Check

#### `GET /`
Основной health check endpoint.

**Ответ:**
```json
{
  "message": "Hello World!"
}
```

**Коды ответов:**
- `200` - Сервис работает

**Пример:**
```bash
curl http://localhost:5000/
```

---

### 2. Управление пользователями

#### `GET /users`
Получить список всех пользователей.

**Ответ:**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  {
    "id": 2,
    "username": "jane_smith", 
    "email": "jane@example.com"
  }
]
```

**Коды ответов:**
- `200` - Успешно

**Пример:**
```bash
curl http://localhost:5000/users
```

#### `POST /users`
Создать нового пользователя.

**Тело запроса:**
```json
{
  "username": "new_user",
  "email": "user@example.com"
}
```

**Ответ:**
```json
{
  "id": 3,
  "username": "new_user",
  "email": "user@example.com"
}
```

**Коды ответов:**
- `201` - Пользователь создан
- `400` - Неверные данные
- `409` - Пользователь уже существует

**Пример:**
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com"}'
```

---

## 📁 Управление файлами

### 3. Загрузка файлов

#### `POST /files/upload`
Загрузить файл в Object Storage.

**Параметры:**
- `file` (multipart/form-data) - Файл для загрузки

**Ограничения:**
- Максимальный размер: 16 MB
- Разрешенные типы: `txt`, `pdf`, `png`, `jpg`, `jpeg`, `gif`, `doc`, `docx`

**Ответ:**
```json
{
  "message": "Файл успешно загружен",
  "filename": "20250906_123456_abc123.txt",
  "original_name": "document.txt",
  "size": 1024,
  "content_type": "text/plain",
  "download_url": "https://storage.example.com/presigned-url",
  "file_info": {
    "name": "20250906_123456_abc123.txt",
    "size": 1024,
    "last_modified": "2025-09-06T12:34:56Z",
    "content_type": "text/plain",
    "etag": "d41d8cd98f00b204e9800998ecf8427e",
    "metadata": {
      "original_name": "document.txt",
      "upload_time": "2025-09-06T12:34:56.789Z",
      "file_size": "1024",
      "content_type": "text/plain"
    }
  }
}
```

**Коды ответов:**
- `201` - Файл загружен
- `400` - Неверный запрос (нет файла, неподдерживаемый тип, превышен размер)
- `500` - Ошибка сервера

**Пример:**
```bash
curl -X POST http://localhost:5000/files/upload \
  -F "file=@document.txt"
```

### 4. Список файлов

#### `GET /files`
Получить список загруженных файлов.

**Query параметры:**
- `prefix` (string, опционально) - Префикс для фильтрации файлов
- `limit` (integer, опционально) - Максимальное количество файлов (по умолчанию 100, максимум 1000)

**Ответ:**
```json
{
  "files": [
    {
      "name": "20250906_123456_abc123.txt",
      "size": 1024,
      "last_modified": "2025-09-06T12:34:56Z",
      "etag": "d41d8cd98f00b204e9800998ecf8427e",
      "download_url": "https://storage.example.com/presigned-url"
    }
  ],
  "count": 1,
  "prefix": ""
}
```

**Коды ответов:**
- `200` - Успешно
- `500` - Ошибка сервера

**Примеры:**
```bash
# Все файлы
curl http://localhost:5000/files

# Файлы с префиксом
curl http://localhost:5000/files?prefix=images/

# Ограничение количества
curl http://localhost:5000/files?limit=10
```

### 5. Информация о файле

#### `GET /files/{filename}/info`
Получить подробную информацию о файле.

**Параметры пути:**
- `filename` (string) - Имя файла

**Ответ:**
```json
{
  "name": "20250906_123456_abc123.txt",
  "size": 1024,
  "last_modified": "2025-09-06T12:34:56Z",
  "content_type": "text/plain",
  "etag": "d41d8cd98f00b204e9800998ecf8427e",
  "metadata": {
    "original_name": "document.txt",
    "upload_time": "2025-09-06T12:34:56.789Z",
    "file_size": "1024",
    "content_type": "text/plain"
  },
  "download_url": "https://storage.example.com/presigned-url"
}
```

**Коды ответов:**
- `200` - Успешно
- `404` - Файл не найден
- `500` - Ошибка сервера

**Пример:**
```bash
curl http://localhost:5000/files/20250906_123456_abc123.txt/info
```

### 6. Скачивание файла

#### `GET /files/{filename}/download`
Получить ссылку для скачивания файла.

**Параметры пути:**
- `filename` (string) - Имя файла

**Ответ:**
```json
{
  "download_url": "https://storage.example.com/presigned-url",
  "file_info": {
    "name": "20250906_123456_abc123.txt",
    "size": 1024,
    "last_modified": "2025-09-06T12:34:56Z",
    "content_type": "text/plain",
    "etag": "d41d8cd98f00b204e9800998ecf8427e"
  },
  "expires_in": 300
}
```

**Коды ответов:**
- `200` - Успешно
- `404` - Файл не найден
- `500` - Ошибка сервера

**Пример:**
```bash
curl http://localhost:5000/files/20250906_123456_abc123.txt/download
```

### 7. Удаление файла

#### `DELETE /files/{filename}`
Удалить файл из Object Storage.

**Параметры пути:**
- `filename` (string) - Имя файла

**Ответ:**
```json
{
  "message": "Файл успешно удален",
  "filename": "20250906_123456_abc123.txt"
}
```

**Коды ответов:**
- `200` - Файл удален
- `404` - Файл не найден
- `500` - Ошибка сервера

**Пример:**
```bash
curl -X DELETE http://localhost:5000/files/20250906_123456_abc123.txt
```

---

## 🔍 Мониторинг

### 8. Storage Health Check

#### `GET /health/storage`
Проверить состояние Object Storage.

**Ответ (здоровое состояние):**
```json
{
  "status": "healthy",
  "message": "Object Storage доступен",
  "timestamp": "2025-09-06T12:34:56.789Z"
}
```

**Ответ (нездоровое состояние):**
```json
{
  "status": "unhealthy", 
  "message": "Object Storage недоступен",
  "timestamp": "2025-09-06T12:34:56.789Z"
}
```

**Коды ответов:**
- `200` - Storage доступен
- `503` - Storage недоступен
- `500` - Ошибка проверки

**Пример:**
```bash
curl http://localhost:5000/health/storage
```

---

## ❌ Обработка ошибок

### Стандартные коды ошибок

- `400 Bad Request` - Неверный запрос
- `401 Unauthorized` - Не авторизован (в будущих версиях)
- `403 Forbidden` - Доступ запрещен (в будущих версиях)
- `404 Not Found` - Ресурс не найден
- `409 Conflict` - Конфликт (например, пользователь уже существует)
- `413 Payload Too Large` - Файл слишком большой
- `415 Unsupported Media Type` - Неподдерживаемый тип файла
- `429 Too Many Requests` - Превышен лимит запросов
- `500 Internal Server Error` - Внутренняя ошибка сервера
- `503 Service Unavailable` - Сервис недоступен

### Формат ошибок

```json
{
  "error": "Описание ошибки",
  "details": "Дополнительные детали (опционально)",
  "code": "ERROR_CODE (опционально)"
}
```

**Примеры ошибок:**

```json
// Файл не найден
{
  "error": "Файл не найден"
}

// Неподдерживаемый тип файла
{
  "error": "Недопустимый тип файла",
  "allowed_extensions": ["txt", "pdf", "png", "jpg", "jpeg", "gif", "doc", "docx"]
}

// Файл слишком большой
{
  "error": "Файл слишком большой",
  "max_size_mb": 16
}

// Внутренняя ошибка
{
  "error": "Внутренняя ошибка сервера"
}
```

---

## 🔒 Rate Limiting

API использует rate limiting для защиты от злоупотреблений:

- **Общие API endpoints**: 10 запросов/секунду на IP
- **Загрузка файлов**: 5 запросов/минуту на IP
- **Burst**: Разрешено до 20 запросов в очереди

При превышении лимита возвращается статус `429 Too Many Requests`.

---

## 📝 Примеры использования

### JavaScript (Fetch API)

```javascript
// Получить список пользователей
async function getUsers() {
  const response = await fetch('http://localhost:5000/users');
  const users = await response.json();
  return users;
}

// Создать пользователя
async function createUser(username, email) {
  const response = await fetch('http://localhost:5000/users', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, email }),
  });
  const user = await response.json();
  return user;
}

// Загрузить файл
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:5000/files/upload', {
    method: 'POST',
    body: formData,
  });
  const result = await response.json();
  return result;
}
```

### Python (requests)

```python
import requests

# Получить список пользователей
def get_users():
    response = requests.get('http://localhost:5000/users')
    return response.json()

# Создать пользователя
def create_user(username, email):
    data = {'username': username, 'email': email}
    response = requests.post('http://localhost:5000/users', json=data)
    return response.json()

# Загрузить файл
def upload_file(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:5000/files/upload', files=files)
    return response.json()
```

### curl

```bash
# Получить пользователей
curl http://localhost:5000/users

# Создать пользователя
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com"}'

# Загрузить файл
curl -X POST http://localhost:5000/files/upload \
  -F "file=@document.pdf"

# Получить список файлов
curl http://localhost:5000/files

# Скачать файл
curl http://localhost:5000/files/filename.pdf/download

# Удалить файл
curl -X DELETE http://localhost:5000/files/filename.pdf
```

---

## 🔮 Планируемые изменения

### v2.0 (планируется)
- JWT аутентификация
- Пагинация для списков
- Поиск по файлам
- Теги для файлов
- API версионирование

### v2.1 (планируется)
- WebSocket поддержка
- Bulk операции
- Расширенные фильтры
- Аналитика использования

---

## 📞 Поддержка

Если у вас есть вопросы по API:

1. Проверьте эту документацию
2. Запустите health checks
3. Проверьте логи приложения
4. Обратитесь в поддержку с примером запроса

**Контакты:**
- Email: api-support@yourcompany.com
- Slack: #api-support
- GitHub Issues: https://github.com/your-repo/issues

---

**API готово к использованию!** 🚀