# Task Manager with Telegram Notifications

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![Pydantic](https://img.shields.io/badge/pydantic-%23E92063.svg?style=for-the-badge&logo=pydantic&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23D71F00.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white)  ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white) ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)

## 🌟Что делает этот проект?
> *Это умный менеджер задач, который сам напоминает о себе там, где вы точно не пропустите уведомление — в Telegram.*

Вы просто создаёте задачу в браузере на Frontend, указываете, через сколько минут напомнить, и продолжаете заниматься своими делами. Бэкенд на FastAPI бережно хранит всё в PostgreSQL, а фоновый планировщик в нужный момент «стучится» в Telegram. 

## 🤖 Telegram уведомления
Бот проверяет статусы задач и присылает уведомление в Telegram по окончанию действия таймера.
Задача автоматически помечается как выполненная (или неудачная, если бот не смог отправить сообщение).


## 🚀 Стек технологий
- **Python** - язык программирования
- **FastAPI** — веб-фреймворк для API
- **PostgreSQL** — основная база данных
- **SQLAlchemy (ORM)** — работа с БД
- **Pydantic** — валидация данных и схемы
- **Docker** — контейнеризация PostgreSQL
- **Telegram Bot API (pyTelegramBotAPI)** — отправка уведомлений
- **Python-dotenv** — управление переменными окружения
- **Uvicorn** — ASGI сервер
- **React** - Frontend
- **Asyncio** — фоновые задачи

## 🗄️ Структура проекта
```bash
src/
├── api/
│   ├── router.py          # эндпоинты
│   └── repository.py      # работа с БД
├── models/
│   ├── models.py          # SQLAlchemy ORM
│   └── constants.py       # ограничения полей
├── schemas/
│   └── schemas.py         # Pydantic схемы
├── bot/
│   └── bot_load.py        # логика бота и планировщик
├── core/
│   └── database.py        # подключение к БД
└── main.py                # точка входа, lifespan
/todo-app-frontend         # фронтэнд проекта
```

## 📦 Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone git@github.com:YoFaceQT/Notes-and-Notifications.git
```

### 2. Создать и активировать виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить переменные окружения,  в корне проекта создать .env

```Создайте файл .env в корне проекта и укажите токены для бота:
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 5. Запустить PostgreSQL через Docker
```bash
docker run --name pg-container -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 postgres
```

### 6. Запустить приложения
Находять в корневой директории проекта:
```bash
uvicorn src.main:app --reload
```
Базовый URL BACKEND: http://localhost:8000


Находясь в директории todo-app-frontend, последовательно запустить команды для фронтэнда:
```bash
npm install
npm start
```
Базовый URL FRONTEND: http://localhost:3000

Документация сгенерирована FASTAPI и находится по адресу: http://localhost:8000/docs

### 📡 API Endpoints

| Method | Endpoint       | Description               |
|--------|----------------|---------------------------|
| POST   | `/tasks`       | Создать новую задачу      |
| GET    | `/tasks`       | Список всех задач         |
| PATCH  | `/tasks/{id}`  | Обновить задачу           |
| DELETE | `/tasks/{id}`  | Удалить задачу            |

### Примеры запроса к API 
Запрос:
```
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Купить молоко",
    "description": "Выйти до 20:00",
    "remind_after_minutes": 30
  }'
```
Ответ: (JSON)
```
[
  {
    "id": 1,
    "name": "Купить молоко",
    "description": "Выйти до 20:00",
    "remind_after_minutes": 30,
    "time_stamp": "2025-04-22T12:00:00",
    "status": "IN_PROGRESS",
    "reminded": false
  }
]
```
