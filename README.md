Flask API с PostgreSQL и Docker
Простое REST API на Flask с PostgreSQL в Docker контейнерах. Проект включает в себя CI/CD pipeline через GitHub Actions и скрипт бэкапа базы данных.

```
flask-api-project/
├── app/                # Исходный код приложения
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   └── routes.py
├── tests/              # Тесты
│   └── test_api.py
├── docker-compose.yml  # Конфигурация Docker Compose
├── Dockerfile          # Docker образ приложения
├── requirements.txt    # Зависимости Python
├── backup_script.sh    # Скрипт бэкапа БД
└── .github/            # Конфигурация GitHub Actions
    └── workflows/
        └── ci-cd.yml     
```

Запуск проекта
Клонируйте репозиторий: git clone https://github.com/ваш-username/flask-api-project.git
cd flask-api-project
Запустите приложение:
docker-compose up --build

Проверьте работу API:
curl http://localhost:5000/
# Должен вернуться ответ: {"message":"Hello World!"}

# Проверка получения пользователей
curl http://localhost:5000/users

# Создание пользователя
curl -X POST http://localhost:5000/users -H "Content-Type: application/json" -d '{"username":"test","email":"test@example.com"}'

API endpoints
GET / - Главная страница
GET /users - Получить всех пользователей
POST /users - Создать нового пользователя

Бэкапы базы данных
Бэкапы PostgreSQL автоматически создаются в папке /backups. Для ручного создания бэкапа:
# Запустите из корня проекта
docker-compose exec web ./backup_script.sh

# Проверьте созданные бэкапы
docker-compose exec db ls -la /backups

CI/CD Pipeline
При пуше в ветку main автоматически:

Собирается Docker образ
Запускаются тесты
Приложение деплоится на сервер
Настройка GitHub Secrets
Для работы CI/CD необходимо добавить следующие секреты в репозитории GitHub:

DOCKERHUB_USERNAME - ваш логин DockerHub
DOCKERHUB_TOKEN - токен DockerHub
SERVER_HOST - IP сервера для деплоя
SERVER_USER - пользователь для SSH
SERVER_SSH_KEY - приватный SSH ключ (без пароля)
















