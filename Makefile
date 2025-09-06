.PHONY: help install test lint format clean run docker-build docker-run

help:  ## Показать помощь
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Установить зависимости
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

test:  ## Запустить тесты
	. venv/bin/activate && python -m pytest tests/ -v

test-cov:  ## Запустить тесты с покрытием
	. venv/bin/activate && coverage run -m pytest tests/
	. venv/bin/activate && coverage report --show-missing
	. venv/bin/activate && coverage html

lint:  ## Проверить код линтером
	. venv/bin/activate && flake8 app/ tests/
	. venv/bin/activate && bandit -r app/

format:  ## Отформатировать код
	. venv/bin/activate && black app/ tests/
	. venv/bin/activate && isort app/ tests/

security:  ## Проверить безопасность
	. venv/bin/activate && safety check -r requirements.txt
	. venv/bin/activate && bandit -r app/

clean:  ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -f *.db

run:  ## Запустить приложение локально
	. venv/bin/activate && python run.py

docker-build:  ## Собрать Docker образ
	docker build -t flask-api .

docker-run:  ## Запустить приложение в Docker
	docker run -p 5000:5000 --name flask-api flask-api

docker-stop:  ## Остановить Docker контейнер
	docker stop flask-api || true
	docker rm flask-api || true

ci:  ## Запустить полную проверку (как в CI)
	make lint
	make security
	make test
	make docker-build

dev-setup:  ## Настроить окружение разработки
	make install
	. venv/bin/activate && pip install pre-commit black isort flake8 bandit safety coverage
	. venv/bin/activate && pre-commit install