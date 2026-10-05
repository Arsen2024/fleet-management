# Fleet Management System

Система керування автопарком, розроблена на Python з використанням FastAPI та PostgreSQL.

Проєкт реалізує автентифікацію користувачів, рольову модель доступу, керування транспортними засобами та розділення конфігурацій для тестового (Sandbox) і робочого (Production) середовищ.

## Технології

* Python 3.13+
* FastAPI
* SQLAlchemy
* PostgreSQL
* asyncpg
* Pydantic / pydantic-settings
* JWT
* pwdlib + Argon2
* pytest
* Ruff
* Docker
* GitHub Actions

## Налаштування середовища

Проєкт підтримує два окремих середовища:

* **Sandbox** — для розробки та тестування;
* **Production** — для робочого середовища.

Вибір середовища виконується через змінну:

```text
ENVIRONMENT
```

Якщо використовується:

```text
ENVIRONMENT=sandbox
```

завантажується `.env.sandbox`.

Для:

```text
ENVIRONMENT=production
```

завантажується `.env.production`.

### Sandbox

Sandbox використовує окрему базу даних:

```text
fleet_db_sandbox
```

та має:

```text
DEBUG=true
```

### Production

Production використовує окрему базу даних:

```text
fleet_db_production
```

та має:

```text
DEBUG=false
```

Таким чином, тестові дані із Sandbox не потрапляють до Production.

## Змінні середовища

Приклад структури `.env.sandbox`:

```env
DATABASE_URL=postgresql+asyncpg://fleet_user:<password>@localhost:5432/fleet_db_sandbox
SECRET_KEY=<sandbox-secret-key>
DEBUG=true
```

Приклад структури `.env.production`:

```env
DATABASE_URL=postgresql+asyncpg://fleet_user:<password>@localhost:5432/fleet_db_production
SECRET_KEY=<production-secret-key>
DEBUG=false
```

Файли з реальними секретами не повинні потрапляти до Git-репозиторію.

До Git не додаються:

```text
.env
.env.sandbox
.env.production
```

Для Production та Sandbox використовуються різні секретні ключі JWT.

## Запуск PostgreSQL

PostgreSQL запускається в Docker-контейнері.

Перевірити запущені контейнери:

```powershell
docker ps
```

Запустити контейнер PostgreSQL:

```powershell
docker start fleet_postgres
```

За необхідності переглянути логи:

```powershell
docker logs fleet_postgres
```

У PostgreSQL використовуються окремі бази:

```text
fleet_db_sandbox
fleet_db_production
```

## Встановлення залежностей

Створити та активувати віртуальне середовище:

```powershell
py -m venv .venv
```

```powershell
.venv\Scripts\Activate.ps1
```

Встановити залежності:

```powershell
py -m pip install -r requirements.txt
```

## Запуск Sandbox

Для запуску тестового середовища в PowerShell:

```powershell
$env:ENVIRONMENT="sandbox"
```

Перевірити конфігурацію:

```powershell
py -c "from app.config import settings; print('DEBUG =', settings.debug); print('DATABASE =', settings.database_url)"
```

Очікується:

```text
DEBUG = True
```

та підключення до:

```text
fleet_db_sandbox
```

Запустити застосунок:

```powershell
uvicorn app.main:app --reload
```

Після запуску API доступний за адресою:

```text
http://127.0.0.1:8000
```

Swagger документація:

```text
http://127.0.0.1:8000/docs
```

## Запуск Production

Встановити Production-середовище:

```powershell
$env:ENVIRONMENT="production"
```

Перевірити конфігурацію:

```powershell
py -c "from app.config import settings; print('DEBUG =', settings.debug); print('DATABASE =', settings.database_url)"
```

Очікується:

```text
DEBUG = False
```

та підключення до:

```text
fleet_db_production
```

Запустити застосунок:

```powershell
uvicorn app.main:app
```

## Автентифікація

Система використовує JWT для автентифікації.

### Реєстрація

```http
POST /auth/register
```

Приклад:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123"
}
```

### Авторизація

```http
POST /auth/login
```

У відповідь користувач отримує JWT access token.

Для доступу до захищених endpoint необхідно використовувати:

```text
Authorization: Bearer <access_token>
```

## Користувачі та ролі

У системі передбачено дві ролі:

* `user`
* `admin`

Звичайний користувач може працювати лише зі своїми ресурсами.

Адміністратор має доступ до адміністративних endpoint.

Система також захищає від IDOR — користувач не може змінювати транспортний засіб іншого користувача лише шляхом зміни його ID.

## Транспортні засоби

Основні endpoint:

```text
POST  /vehicles
GET   /vehicles
PATCH /vehicles/{vehicle_id}/status
```

Кожен транспортний засіб прив'язаний до конкретного користувача.

## Обробка помилок

Production-середовище використовує:

```text
DEBUG=false
```

Для внутрішніх помилок сервера використовується узагальнена відповідь:

```json
{
  "detail": "Internal server error"
}
```

Це дозволяє не розкривати користувачу внутрішні деталі та traceback застосунку.

## Тестування

Для запуску тестів:

```powershell
py -m pytest -v
```

Поточний набір тестів перевіряє:

* успішний login;
* login з неправильним паролем;
* доступ анонімного користувача;
* заборону доступу звичайного користувача до admin endpoint;
* захист від доступу до чужого транспортного засобу;
* хешування паролів;
* перевірку паролів;
* створення JWT.

## Перевірка якості коду

Для запуску Ruff:

```powershell
py -m ruff check .
```

## CI/CD

Проєкт використовує GitHub Actions для автоматичної перевірки коду.

Pipeline виконується при:

* push у `main`;
* створенні або оновленні Pull Request у `main`.

CI pipeline виконує:

1. встановлення Python;
2. встановлення залежностей;
3. запуск Ruff;
4. запуск автоматичних тестів pytest;
5. використання окремої PostgreSQL бази для CI.

Мета CI/CD — автоматично перевіряти код перед інтеграцією змін у головну гілку.

## Безпека конфігурації

Секретні дані не зберігаються безпосередньо в Python-коді.

Зокрема, з коду винесені:

* URL бази даних;
* пароль бази даних;
* JWT `SECRET_KEY`;
* режим `DEBUG`.

Конфігурація завантажується через `pydantic-settings`.

Для різних середовищ використовуються окремі конфігурації та окремі бази даних.

**Реальні паролі, секретні ключі та інші конфіденційні значення не повинні публікуватися в Git-репозиторії.**