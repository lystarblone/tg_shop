# E-COMMERCE Telegram Bot

Это Telegram-бот для интернет-магазина, реализующий функционал каталога товаров, корзины, оформления заказов и базовой админ-панели. Построен на базе Aiogram 3.x, SQLAlchemy (PostgreSQL), Redis для хранения корзин.

## Функциональность

- **Каталог товаров**:
  - Просмотр списка категорий (/catalog).
  - Просмотр товаров в категории с ценами и описанием.
  - Детальная информация о товаре (название, описание, цена; фото в разработке).
  - Навигация через inline-клавиатуру.
- **Корзина**:
  - Добавление товаров (/cart, кнопка "Добавить в корзину").
  - Просмотр содержимого с итоговой суммой.
  - Очистка корзины (кнопка "Очистить корзину").
  - *В разработке*: изменение количества, удаление отдельных товаров.
- **Оформление заказа**:
  - Сбор данных: имя, телефон, адрес.
  - Выбор доставки: курьер или самовывоз.
  - Подтверждение заказа с уникальным номером.
- **Админ-панель** (в разработке):
  - Команды: /addproduct, /editproduct, /setstatus.
  - Просмотр всех заказов и изменение их статусов.
- **Команды**:
  - /start — приветственное сообщение.
  - /catalog — просмотр категорий.
  - /cart — просмотр корзины.
  - /orders — список заказов пользователя.
  - /addproduct, /editproduct, /setstatus — админ-команды.

## Технологии

- Python 3.10+
- Aiogram 3.x (асинхронный Telegram API)
- SQLAlchemy + AsyncPG (PostgreSQL)
- Redis (корзина)
- Pydantic v2 (валидация данных)
- pytest, pytest-asyncio (тестирование)
- Logging (журналирование)

## Архитектура

Проект построен по многослойной архитектуре с разделением ответственности:

1. **Handlers** (`app/handlers/`):
   - Обработчики Telegram-событий (команды, callback).
   - Используют FSM (Finite State Machine) для оформления заказа.
   - Примеры: `catalog.py` (каталог), `cart.py` (корзина), `order.py` (заказы).

2. **Services** (`app/services/`):
   - Бизнес-логика: `CartService` (управление корзиной в Redis), `user_service`, `product_service`, `order_service`.
   - Выполняют высокоуровневые операции, взаимодействуя с репозиториями.

3. **Repositories** (`app/repositories/`):
   - CRUD-операции с БД (PostgreSQL) через SQLAlchemy.
   - Примеры: `user_repository`, `product_repository`, `order_repository`.

4. **Models** (`app/models/`):
   - SQLAlchemy-модели для таблиц: User, Product, Category, Order, OrderItem.
   - Определяют структуру БД.

5. **Schemas** (`app/schemas/`):
   - Pydantic-модели для валидации данных (UserCreate, ProductCreate, OrderCreate).

6. **Core** (`app/core/`):
   - Конфигурация (settings), запуск бота (main.py), подключение к Redis.

7. **Utils** (`app/utils/`):
   - Вспомогательные функции: генерация номеров заказов, логирование.

**Паттерны**:
- **Repository Pattern**: отделяет доступ к данным от бизнес-логики.
- **Service Layer**: централизует бизнес-логику.
- **FSM**: управляет процессом оформления заказа.

**Хранение данных**:
- **PostgreSQL**: пользователи, товары, категории, заказы.
- **Redis**: временное хранение корзин (ключ `cart:<user_id>`).

## Схема базы данных

```
Users
├── id (PK, Integer)
├── telegram_id (Integer, unique)
├── username (String, nullable)
├── name (String, nullable)
└── is_admin (Boolean, default=False)

Categories
├── id (PK, Integer)
├── name (String, not null)
└── description (Text, nullable)

Products
├── id (PK, Integer)
├── sku (String, unique, not null)
├── name (String, not null)
├── description (Text, nullable)
├── price (Numeric(10,2), not null)
├── currency (String(3), default="USD")
├── quantity (Integer, default=0)
├── category_id (FK to Categories.id, nullable)
├── photo_url (Text, nullable)
├── created_at (DateTime)
└── updated_at (DateTime)

Orders
├── id (PK, Integer)
├── user_id (FK to Users.id, not null)
├── status (String(50), default="pending")
├── total_price (Float, not null)
├── delivery_address (String(255), nullable)
├── contact_phone (String(20), nullable)
└── created_at (DateTime)

OrderItems
├── id (PK, Integer)
├── order_id (FK to Orders.id, not null)
├── product_id (FK to Products.id, not null)
├── quantity (Integer, not null)
└── price (Float, not null)
```

## Настройка базы данных

1. Установите PostgreSQL:
   ```bash
   sudo apt update
   sudo apt install postgresql
   ```

2. Создайте базу данных:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE ecommerce;
   CREATE USER user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE ecommerce TO user;
   \q
   ```

3. Настройте `.env` с DATABASE_URL:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ecommerce
   ```

4. При запуске бота таблицы создаются автоматически (`init_models` в `app/models/db.py`).

## Установка и запуск локально

1. **Клонируйте репозиторий**:
   ```bash
   git clone <repo-url>
   cd ecommerce-bot
   ```

2. **Создайте виртуальное окружение**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте .env**:
   Создайте файл `.env`:
   ```
   BOT_TOKEN=your_telegram_bot_token
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ecommerce
   REDIS_URL=redis://localhost:6379/0
   ADMIN_IDS=123456789,987654321
   ```

5. **Запустите Redis**:
   ```bash
   sudo apt install redis-server
   redis-server
   ```

6. **Запустите бот**:
   ```bash
   python app/core/main.py
   ```

## Запуск с Docker

1. Убедитесь, что Docker и Docker Compose установлены:
   ```bash
   docker --version
   docker-compose --version
   ```

2. Создайте `.env` (см. выше).

3. Запустите:
   ```bash
   docker-compose up -d --build
   ```

4. Проверьте логи:
   ```bash
   docker-compose logs -f bot
   ```

## Примеры использования команд

1. **Запуск бота**:
   - Команда: `/start`
   - Ответ:
     ```
     👋 Добро пожаловать в наш E-COMMERCE бот!
     Я помогу вам удобно покупать товары прямо здесь! Вы можете:
     🛍 Просматривать каталог товаров
     🛒 Добавлять товары в корзину
     📦 Оформлять заказы и отслеживать их статус
     Чтобы начать выбирать товары, нажмите /catalog
     ```

2. **Просмотр каталога**:
   - Команда: `/catalog`
   - Ответ: Список категорий (например, "Электроника", "Одежда") с inline-кнопками.

3. **Просмотр корзины**:
   - Команда: `/cart`
   - Ответ:
     ```
     📦 Ваша корзина:
     Смартфон × 1 = 30000 ₽
     Наушники × 2 = 6000 ₽
     Итого: 36000 ₽
     ```
     Кнопки: "Оформить заказ", "Очистить корзину".

4. **Оформление заказа**:
   - Нажмите "Оформить заказ" в корзине.
   - Введите имя, телефон, адрес, выберите доставку.
   - Ответ:
     ```
     ✅ Заказ #ORD-123456-ABC123 оформлен!
     Имя: Иван Иванов
     Телефон: +79991234567
     Адрес: Москва, ул. Ленина, 10
     Доставка: Курьер
     Сумма: 36000 ₽
     ```

5. **Просмотр заказов**:
   - Команда: `/orders`
   - Ответ:
     ```
     📦 Ваши заказы:
     Заказ #1 - Статус: pending - Сумма: 36000 ₽
     ─────────────────────────
     Заказ #2 - Статус: shipped - Сумма: 15000 ₽
     ```

## Тестирование

Проект включает unit-тесты для основных функций. Тесты находятся в `tests/`.

### Установка зависимостей для тестов

```bash
pip install pytest pytest-asyncio fakeredis
```

### Запуск тестов

```bash
pytest tests/ -v
```

### Пример теста (`tests/test_cart_service.py`)

```python
import pytest
from app.services.cart_service import CartService
from unittest.mock import AsyncMock, patch
import fakeredis.aioredis

@pytest.mark.asyncio
async def test_add_to_cart():
    with patch('app.services.cart_service.aioredis.from_url', return_value=fakeredis.aioredis.FakeRedis(decode_responses=True)):
        cart_service = CartService()
        user_id = 123
        product_id = 1
        await cart_service.clear_cart(user_id)
        result = await cart_service.add_item(user_id, product_id, quantity=2)
        assert result is True
        cart = await cart_service.get_cart(user_id)
        assert cart == {"1": 2}
```

### Покрытие тестов

- `test_add_to_cart`: Проверяет добавление товара в корзину.
- `test_get_empty_cart`: Проверяет получение пустой корзины.
- `test_add_nonexistent_product`: Проверяет обработку ошибки при добавлении несуществующего товара.