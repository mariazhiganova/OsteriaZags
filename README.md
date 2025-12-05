# "Osteria Zags"- Веб приложение для бронирования столиков

Сайт ресторана, который обеспечивает краткой информацией о самом ресторане, а также дает возможность бронирования
столиков.

## Возможности

- Создание личного кабинета, бронирований
- Динамический выбор стола
- Просмотр истории посещений
- Управление контентом через админку

## Технологии

- **Backend**: Django
- **Database**: PostgreSQL
- **Task Queue**: Celery + Redis
- **Notifications**: Email
- **Containerization**: Docker + Docker Compose
- **Frontend:** Bootstrap 5, JavaScript (AJAX)

# Установка и запуск

### Клонирование репозитория

```bash
git clone git@github.com:mariazhiganova/OsteriaZags.git
```

### Настройка окружения

Создайте файл .env на основе .env.example

### Установка зависимостей

```
poetry install
poetry shell
```

## Установка через Docker (рекомендуется)

### 1. Выполните команду

```
docker-compose up -d
```

### 2. Проверьте статус и работоспособность

```
docker-compose ps
```

#### Должны быть в статусе Up:

- web - основное приложение
- db - база данных
- redis - брокер celery
- celery
- celery-beat - периодические задачи

#### Проверить логи можно следующей командой:

```
docker-compose logs
```

#### Перейти по ссылке (должна открываться главная страница)

http://localhost:8000/

### 3. Остановка

```
docker-compose down
```

## Ручной запуск (без Docker)

### 1. Установите зависимости

```
poetry install
poetry shell
```

### 2. Запустите сервер

```
python manage.py migrate
python manage.py runserver
```

### 3. Celery и celery-beat (в отдельном терминале)

```
-A config worker -l INFO
-A config beat -l INFO
```

## Автор

**Мария Жиганова** - Backend Developer (Python)

```
GitHub - https://github.com/mariazhiganova
```
