<!-- DVO-L3-7F2A91 -->

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

## Kubernetes (Minikube)

Проєкт підтримує розгортання в Kubernetes за допомогою Minikube. Kubernetes-конфігурація розташована в директорії `k8s/`.

### Архітектура Kubernetes

У Kubernetes розгортаються такі компоненти:

| Компонент | Призначення |
|---|---|
| Fleet Management | Основний FastAPI-застосунок |
| Telemetry | Сервіс обробки телеметрії |
| Fleet PostgreSQL | База даних основного застосунку |
| Telemetry PostgreSQL | База даних телеметрії |
| Redis | Кешування та допоміжні операції |

Для основного застосунку та Telemetry використовуються окремі Deployment з двома репліками кожен.

PostgreSQL використовує PersistentVolumeClaim для збереження даних між перезапусками Pod.

### Структура Kubernetes-маніфестів

У директорії `k8s/` розміщені окремі YAML-файли:

- `00-namespace.yaml` — Namespace проєкту;
- `01-configmap.yaml` — несекретні параметри конфігурації;
- `02-secret.yaml` — секретні параметри;
- `03-04-pvc-*.yaml` — сховища PostgreSQL;
- `05-08-*-postgres.yaml` — Deployment і Service баз даних;
- `09-10-*-redis.yaml` — Deployment і Service Redis;
- `11-12-*-telemetry.yaml` — Deployment і Service Telemetry;
- `13-14-*-fleet-management.yaml` — Deployment і Service основного застосунку.

Усі ресурси розміщуються в Namespace `fleet-management`.

### Вимоги

Для розгортання необхідні:

- Docker Desktop;
- Minikube;
- kubectl;
- доступ до опублікованих контейнерних образів GHCR.

### Запуск Minikube

Запуск кластера з Docker driver:

```powershell
minikube start --driver=docker
```

Увімкнення metrics-server та ingress:

```powershell
minikube addons enable metrics-server
minikube addons enable ingress
```

Перевірка стану кластера:

```powershell
kubectl get nodes
kubectl get pods -n kube-system
```

### Розгортання застосунку

Перебуваючи в кореневій директорії проєкту, виконати:

```powershell
kubectl apply -f k8s/
```

Перевірити створені ресурси:

```powershell
kubectl get all,pvc -n fleet-management
```

Перевірити стан Deployment:

```powershell
kubectl get deployments -n fleet-management
```

Перевірити стан PersistentVolumeClaim:

```powershell
kubectl get pvc -n fleet-management
```

### ConfigMap

ConfigMap `fleet-config` містить несекретні параметри конфігурації:

| Параметр | Значення |
|---|---|
| ENVIRONMENT | production |
| DEBUG | false |
| TELEMETRY_SERVICE_URL | http://telemetry-service:8001 |
| REDIS_URL | redis://redis:6379/0 |
| FLEET_MANAGEMENT_URL | http://fleet-management:8000 |

Переглянути ConfigMap:

```powershell
kubectl get configmap fleet-config -n fleet-management -o yaml
```

### Secret

Secret `fleet-secrets` використовується для зберігання чутливих параметрів:

- `FLEET_DB_PASSWORD`;
- `TELEMETRY_DB_PASSWORD`;
- `SECRET_KEY`;
- `SERVICE_API_KEY`;
- `TELEMETRY_DATABASE_URL`;
- `FLEET_DATABASE_URL`.

У лабораторному середовищі використовуються демонстраційні тестові значення. Реальні паролі та ключі не повинні зберігатися у відкритому вигляді в Git-репозиторії.

Переглянути наявність Secret:

```powershell
kubectl get secret fleet-secrets -n fleet-management
```

### Доступ до застосунку

Для основного застосунку створено Service типу NodePort:

- Service: `fleet-management`;
- внутрішній порт: `8000`;
- NodePort: `30080`.

Для отримання адреси доступу:

```powershell
minikube service fleet-management -n fleet-management --url
```

Після виконання команди Minikube надає URL для доступу до застосунку через браузер. У Windows із Docker driver необхідно залишити термінал із запущеною командою відкритим.

### Перевірка ConfigMap та Secret у Pod

Переглянути змінні середовища ConfigMap у Pod:

```powershell
kubectl exec -it <pod-name> -n fleet-management -- printenv ENVIRONMENT
kubectl exec -it <pod-name> -n fleet-management -- printenv DEBUG
kubectl exec -it <pod-name> -n fleet-management -- printenv TELEMETRY_SERVICE_URL
```

Перевірити наявність секретних змінних без виведення їхніх значень:

```powershell
kubectl exec <pod-name> -n fleet-management -- sh -c 'test -n "$SECRET_KEY" && echo SECRET_KEY=present'
```

### Масштабування та самовідновлення

Deployment основного застосунку налаштований на дві репліки.

Перевірка Pod:

```powershell
kubectl get pods -n fleet-management
```

Перевірка самовідновлення: після видалення одного Pod Kubernetes автоматично створює новий.

```powershell
kubectl delete pod <pod-name> -n fleet-management
```

Масштабування до трьох реплік:

```powershell
kubectl scale deployment/fleet-management --replicas=3 -n fleet-management
```

Повернення до двох реплік:

```powershell
kubectl scale deployment/fleet-management --replicas=2 -n fleet-management
```

Перегляд логів обох реплік:

```powershell
kubectl logs -l app=fleet-management --prefix=true --tail=20 -n fleet-management
```

### Rolling Update та Rollback

Для Deployment основного застосунку використовується стратегія `RollingUpdate` з параметрами:

- `maxUnavailable: 0`;
- `maxSurge: 1`.

Це дозволяє створювати нові Pod до видалення старих, зберігаючи доступність застосунку під час оновлення за умови готовності нових реплік.

У GHCR опубліковані версії образів:

- `ghcr.io/arsen2024/fleet-management:1.0.0`;
- `ghcr.io/arsen2024/fleet-management:1.1.0`;
- `ghcr.io/arsen2024/fleet-telemetry:1.0.0`;
- `ghcr.io/arsen2024/fleet-telemetry:1.1.0`.

Для оновлення необхідно змінити тег образу в Deployment YAML та застосувати маніфест:

```powershell
kubectl apply -f k8s/13-deployment-fleet-management.yaml
```

Перевірка процесу оновлення:

```powershell
kubectl rollout status deployment/fleet-management -n fleet-management
```

Перегляд історії:

```powershell
kubectl rollout history deployment/fleet-management -n fleet-management
```

Повернення до попередньої версії:

```powershell
kubectl rollout undo deployment/fleet-management -n fleet-management
```

У межах лабораторної роботи було перевірено оновлення з версії `1.0.0` до `1.1.0` та успішне повернення до `1.0.0`.

### Діагностика несправностей

Для перевірки обробки помилок завантаження образів було використано неіснуючий тег:

```text
ghcr.io/arsen2024/fleet-telemetry:9.9.9
```

У результаті Pod перейшов у стан `ImagePullBackOff`.

Для діагностики використовуються команди:

```powershell
kubectl get pods -n fleet-management
kubectl describe pod <pod-name> -n fleet-management
kubectl get events -n fleet-management --sort-by=.metadata.creationTimestamp
```

Після цього було відновлено правильний тег `1.0.0` та перевірено успішний запуск Telemetry Pod.

Перегляд логів застосунку:

```powershell
kubectl logs deployment/fleet-management -n fleet-management --tail=30
```

### Моніторинг ресурсів

Для отримання інформації про використання ресурсів використовується metrics-server:

```powershell
kubectl top nodes
kubectl top pods -n fleet-management
```

### Особливість виконання вимоги mascot

У додатку A лабораторної роботи вимагається мітка `mascot: кабачок`.

Однак Kubernetes не дозволяє використовувати кириличні символи у значеннях labels. Тому використовується сумісне значення:

```yaml
mascot: kabachok
```

Оригінальний текст `кабачок` збережено в annotation:

```yaml
devops-lab/mascot: "кабачок"
```

Також для всіх створених Kubernetes-об'єктів використовується обов'язкова annotation:

```yaml
devops-lab/mascot-approved: "true"
```

Це дозволяє зберегти зміст вимоги та дотриматися обмежень Kubernetes API.

## Подяки

Автор висловлює щиру подяку кабачку за моральну підтримку.