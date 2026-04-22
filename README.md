# Task Manager with Telegram Notifications

(add your badges here)

## 🌟 Overview
Сервис для управления задачами (заметками) с возможностью устанавливать таймеры и получать напоминания в Telegram. 
BACKEND на FastAPI, PostgreSQL, уведомления через Telegram бота, фоновый планировщик.
FRONTEND на React

## 🤖 Telegram уведомления
Бот проверяет каждые 30 секунд задачи со статусом IN_PROGRESS и reminder_at <= текущее_время.
При срабатывании таймера отправляется сообщение в указанный чат.
Статус задачи меняется на SUCCESSFULLY_SENT (или FAILED_TO_SEND при ошибке отправки).


## 📦 Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
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

### 4. Настроить переменные окружения

```Создайте файл .env в корне проекта и укажите токены для бота:
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 5. Запустить PostgreSQL через Docker
```bash
docker run --name pg-container -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 postgres
```

### 6. Запустить приложение
```bash
Находять в корневой директории проекта:
uvicorn src.main:app --reload
Базовый URL BACKEND: http://localhost:8000
Находясь в директории todo-app-frontend: последовательно запустить команды для фронтэнда:
npm install
npm start
FRONTEND будет доступен на `http://localhost:3000`.


### 📡 API Endpoints

| Method | Endpoint       | Description               |
|--------|----------------|---------------------------|
| POST   | `/tasks`       | Создать новую задачу      |
| GET    | `/tasks`       | Список всех задач         |
| PATCH  | `/tasks/{id}`  | Обновить задачу           |
| DELETE | `/tasks/{id}`  | Удалить задачу            |


### Примеры запросов к API 

bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Купить молоко",
    "description": "Выйти до 20:00",
    "remind_after_minutes": 30
  }'
Ответ (статус 201 Created):

json
{
  "id": 1,
  "name": "Купить молоко",
  "description": "Выйти до 20:00",
  "remind_after_minutes": 30,
  "time_stamp": "2025-04-22T12:00:00",
  "status": "IN_PROGRESS",
  "reminded": false
}
GET /tasks — все задачи
bash
curl http://localhost:8000/tasks
Ответ:

json
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
PATCH /tasks/1 — обновить задачу
bash
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Купить хлеб",
    "remind_after_minutes": 60
  }'
DELETE /tasks/1 — удалить задачу
bash
curl -X DELETE http://localhost:8000/tasks/1
Ответ: статус 204 No Content


## 🚀 Стек технологий

- **FastAPI** — веб-фреймворк для API
- **PostgreSQL** — основная база данных
- **SQLAlchemy (ORM)** — работа с БД
- **Pydantic** — валидация данных и схемы
- **Docker** — контейнеризация PostgreSQL
- **Telegram Bot API (pyTelegramBotAPI)** — отправка уведомлений
- **python-dotenv** — управление переменными окружения
- **Uvicorn** — ASGI сервер
- **asyncio + threading** — фоновые задачи



🗄️ Структура проекта

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
