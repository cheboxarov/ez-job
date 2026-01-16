# Clean Architecture Backend Template

## Обзор

Шаблон архитектуры бэкенда на Python с использованием Clean Architecture. Подходит для FastAPI, но принципы применимы к любому фреймворку.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION                              │
│              (Routers, Handlers, DTOs)                       │
├─────────────────────────────────────────────────────────────┤
│                     APPLICATION                              │
│                (Services, Factories)                         │
├─────────────────────────────────────────────────────────────┤
│                       DOMAIN                                 │
│            (Entities, Use Cases, Ports/Interfaces)           │
├─────────────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE                             │
│        (Repositories, Database, Clients, Auth)               │
└─────────────────────────────────────────────────────────────┘
```

**Направление зависимостей:** внешние слои зависят от внутренних, но не наоборот.

---

## Структура проекта

```
backend/
├── domain/              # Бизнес-логика (ядро)
│   ├── entities/        # Доменные сущности
│   ├── interfaces/      # Порты (абстракции)
│   ├── use_cases/       # Юзкейсы
│   ├── exceptions/      # Доменные исключения
│   └── utils/           # Чистые утилиты
├── application/         # Оркестрация
│   ├── services/        # Сервисы приложения
│   └── factories/       # Фабрики для DI
├── infrastructure/      # Внешние интеграции
│   ├── database/        # БД, репозитории, модели
│   ├── clients/         # HTTP клиенты
│   ├── auth/            # Аутентификация
│   └── events/          # Event Bus
├── presentation/        # API слой
│   ├── routers/         # Роутеры
│   ├── dto/             # Request/Response модели
│   └── dependencies.py  # Dependency Injection
└── main.py              # Точка входа
```

---

## Domain Layer

Ядро приложения. **Не зависит от фреймворков и внешних библиотек.**

### Entities

Чистые Python dataclass-ы:

```python
from dataclasses import dataclass
from uuid import UUID

@dataclass(slots=True)
class User:
    id: UUID
    email: str

@dataclass(slots=True)
class Order:
    id: UUID
    user_id: UUID
    total: Decimal
    status: OrderStatus
```

**Правила:**
- `slots=True` для оптимизации памяти
- Никаких ORM-аннотаций
- Никаких Pydantic моделей
- Только бизнес-атрибуты

### Ports (Interfaces)

Абстракции для внешних зависимостей:

```python
from abc import ABC, abstractmethod

class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

class UnitOfWorkPort(ABC):
    @property
    @abstractmethod
    def user_repository(self) -> UserRepositoryPort: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
```

**Правила:**
- Порт определяет **что** нужно, не **как**
- Каждая внешняя зависимость = отдельный порт
- Используйте ABC для явных контрактов

### Use Cases

Единица бизнес-логики:

```python
class CreateOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        payment_gateway: PaymentGatewayPort,
    ):
        self._orders = order_repository
        self._payments = payment_gateway

    async def execute(self, user_id: UUID, items: list[OrderItem]) -> Order:
        order = Order(
            id=uuid4(),
            user_id=user_id,
            total=sum(item.price for item in items),
            status=OrderStatus.PENDING,
        )

        await self._payments.charge(user_id, order.total)
        order.status = OrderStatus.PAID

        return await self._orders.create(order)
```

**Правила:**
- Одна задача = один use case
- Зависимости через конструктор (порты, не реализации)
- Метод `execute()` как единственная точка входа
- Stateless (без состояния)
- **Никаких импортов из infrastructure**

### Exceptions

Доменные исключения:

```python
class DomainException(Exception):
    """Базовое исключение домена."""
    pass

class EntityNotFoundError(DomainException):
    """Сущность не найдена."""
    pass

class DuplicateEntityError(DomainException):
    """Сущность уже существует."""
    pass

class InsufficientFundsError(DomainException):
    """Недостаточно средств."""
    pass
```

---

## Application Layer

Оркестрирует доменную логику.

### Services

Фасад над юзкейсами:

```python
class OrdersService:
    def __init__(self, unit_of_work: UnitOfWorkPort):
        self._uow = unit_of_work

    async def create_order(self, user_id: UUID, items: list[OrderItem]) -> Order:
        async with self._uow:
            use_case = CreateOrderUseCase(
                self._uow.order_repository,
                self._uow.payment_gateway,
            )
            order = await use_case.execute(user_id, items)
            await self._uow.commit()
            return order
```

**Правила:**
- Управляет транзакциями
- Координирует несколько use cases
- Не содержит бизнес-логику

### Factories

Создание сложных объектов:

```python
class UseCaseFactory:
    def __init__(self, config: AppConfig, unit_of_work: UnitOfWorkPort):
        self._config = config
        self._uow = unit_of_work

    def create_process_payment(self) -> ProcessPaymentUseCase:
        gateway = StripeGateway(self._config.stripe)
        notifier = EmailNotifier(self._config.email)
        return ProcessPaymentUseCase(
            self._uow.payment_repository,
            gateway,
            notifier,
        )
```

**Правила:**
- Централизованное создание use cases
- Внедрение infrastructure зависимостей
- Упрощает тестирование

---

## Infrastructure Layer

Реализует порты домена.

### Database Models

SQLAlchemy модели:

```python
from sqlalchemy.orm import Mapped, mapped_column

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

**Правила:**
- Модели только в infrastructure
- Не использовать в domain или application

### Repositories

Реализация портов:

```python
class UserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    def _to_domain(self, model: UserModel) -> User:
        return User(id=model.id, email=model.email)

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(id=entity.id, email=entity.email)
```

**Правила:**
- Конвертация Model ↔ Entity внутри репозитория
- Возвращать только доменные сущности
- Ловить framework-исключения, бросать доменные

### Unit of Work

Управление транзакциями:

```python
class UnitOfWork(UnitOfWorkPort):
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def __aenter__(self):
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self._session.close()

    @property
    def user_repository(self) -> UserRepositoryPort:
        return UserRepository(self._session)

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
```

### Dual-mode Repositories

Поддержка транзакционного и standalone режимов:

```python
class BaseRepository:
    def __init__(self, session_or_factory: AsyncSession | async_sessionmaker):
        if isinstance(session_or_factory, AsyncSession):
            self._session = session_or_factory
            self._session_factory = None
        else:
            self._session = None
            self._session_factory = session_or_factory

    @asynccontextmanager
    async def _get_session(self):
        if self._session:
            yield self._session
        else:
            async with self._session_factory() as session:
                yield session
                await session.commit()
```

**Использование:**
```python
# Транзакционный режим
async with UnitOfWork(session_factory) as uow:
    await uow.user_repository.create(user)
    await uow.order_repository.create(order)
    await uow.commit()  # Один коммит

# Standalone режим (для длительных операций)
repo = UserRepository(session_factory)
user = await repo.get_by_id(user_id)  # Auto-commit
```

---

## Presentation Layer

HTTP API.

### Dependency Injection

```python
from functools import lru_cache
from fastapi import Depends

@lru_cache()
def get_config() -> AppConfig:
    return load_config()

async def get_unit_of_work() -> AsyncGenerator[UnitOfWorkPort, None]:
    config = get_config()
    uow = UnitOfWork(create_session_factory(config.database))
    async with uow:
        yield uow

def get_orders_service(
    uow: UnitOfWorkPort = Depends(get_unit_of_work),
) -> OrdersService:
    return OrdersService(uow)

def get_use_case_factory(
    config: AppConfig = Depends(get_config),
    uow: UnitOfWorkPort = Depends(get_unit_of_work),
) -> UseCaseFactory:
    return UseCaseFactory(config, uow)
```

### Handlers

```python
@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    service: OrdersService = Depends(get_orders_service),
) -> OrderResponse:
    order = await service.create_order(
        user_id=current_user.id,
        items=request.items,
    )
    return OrderResponse.from_entity(order)
```

**Обязанности handler:**
- Валидация (Pydantic)
- Аутентификация (Depends)
- Делегирование сервисам
- Конвертация Entity → DTO
- Обработка ошибок

**Чего handler НЕ делает:**
- Бизнес-логика
- Прямые запросы к БД
- Создание use cases inline

### DTOs

```python
class CreateOrderRequest(BaseModel):
    items: list[OrderItemRequest]

class OrderResponse(BaseModel):
    id: UUID
    total: Decimal
    status: str
    created_at: datetime

    @classmethod
    def from_entity(cls, entity: Order) -> "OrderResponse":
        return cls(
            id=entity.id,
            total=entity.total,
            status=entity.status.value,
            created_at=entity.created_at,
        )
```

---

## Композиция Use Cases

### Последовательная

```python
class ProcessOrderWithNotificationUseCase:
    def __init__(
        self,
        create_order_uc: CreateOrderUseCase,
        send_notification_uc: SendNotificationUseCase,
    ):
        self._create = create_order_uc
        self._notify = send_notification_uc

    async def execute(self, user_id: UUID, items: list) -> Order:
        order = await self._create.execute(user_id, items)
        await self._notify.execute(user_id, f"Order {order.id} created")
        return order
```

### Параллельная

```python
class BatchProcessUseCase:
    async def execute(self, items: list) -> list:
        tasks = [self._process_item.execute(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]
```

### С кэшированием (Decorator)

```python
class GetDataWithCacheUseCase:
    def __init__(
        self,
        get_from_cache_uc: GetFromCacheUseCase,
        fetch_data_uc: FetchDataUseCase,
        save_to_cache_uc: SaveToCacheUseCase,
    ):
        self._cache = get_from_cache_uc
        self._fetch = fetch_data_uc
        self._save = save_to_cache_uc

    async def execute(self, key: str) -> Data:
        cached = await self._cache.execute(key)
        if cached:
            return cached

        data = await self._fetch.execute(key)
        await self._save.execute(key, data)
        return data
```

---

## Типичные ошибки

### 1. Domain импортирует из Infrastructure

```python
# НЕПРАВИЛЬНО
from infrastructure.clients.http_client import HttpClient

class FetchDataUseCase:
    def __init__(self):
        self._client = HttpClient()  # Жесткая зависимость
```

```python
# ПРАВИЛЬНО
from domain.interfaces.http_client_port import HttpClientPort

class FetchDataUseCase:
    def __init__(self, client: HttpClientPort):
        self._client = client  # Инъекция через порт
```

### 2. SQLAlchemy в Domain

```python
# НЕПРАВИЛЬНО
from sqlalchemy.exc import IntegrityError

class CreateUserUseCase:
    async def execute(self, user: User):
        try:
            await self._repo.create(user)
        except IntegrityError:
            raise DuplicateUserError()
```

```python
# ПРАВИЛЬНО - ловить в репозитории
class UserRepository(UserRepositoryPort):
    async def create(self, user: User) -> User:
        try:
            ...
        except IntegrityError:
            raise DuplicateEntityError()  # Доменное исключение
```

### 3. Создание Use Cases в Handler

```python
# НЕПРАВИЛЬНО
@router.post("/users")
async def create_user(request: CreateUserRequest):
    from infrastructure.clients.email import EmailClient
    client = EmailClient()
    use_case = CreateUserUseCase(client)
    ...
```

```python
# ПРАВИЛЬНО
@router.post("/users")
async def create_user(
    request: CreateUserRequest,
    factory: UseCaseFactory = Depends(get_use_case_factory),
):
    use_case = factory.create_user_use_case()
    ...
```

### 4. Duck Typing вместо интерфейсов

```python
# НЕПРАВИЛЬНО
if hasattr(self._client, 'set_config'):
    self._client.set_config(config)
```

```python
# ПРАВИЛЬНО
class ConfigurableClientPort(ClientPort):
    @abstractmethod
    def set_config(self, config: Config) -> None: ...
```

---

## Паттерны

| Паттерн | Слой | Назначение |
|---------|------|------------|
| **Repository** | Infrastructure | Абстракция доступа к данным |
| **Unit of Work** | Infrastructure | Управление транзакциями |
| **Factory** | Application | Создание сложных объектов |
| **Strategy** | Infrastructure | Разные реализации (клиенты, агенты) |
| **Observer** | Infrastructure | События, уведомления |
| **Decorator** | Domain/Application | Кэширование, логирование |
| **Facade** | Application | Упрощение интерфейса (Services) |

---

## Поток данных

```
1. HTTP Request
       │
       ▼
2. Handler
   • Pydantic валидация
   • Аутентификация
   • DI зависимостей
       │
       ▼
3. Service
   • Управление транзакцией
   • Оркестрация use cases
       │
       ▼
4. Use Case
   • Бизнес-логика
   • Работа с портами
       │
       ▼
5. Repository
   • Entity ↔ Model
   • SQL запросы
       │
       ▼
6. Database
       │
       ▼
7. Entity → DTO → JSON Response
```

---

## Чек-лист

### Domain Layer
- [ ] Entities без ORM/Pydantic аннотаций
- [ ] Порты для всех внешних зависимостей
- [ ] Use cases получают зависимости через конструктор
- [ ] Никаких импортов из infrastructure/application
- [ ] Доменные исключения вместо framework-исключений

### Application Layer
- [ ] Services управляют транзакциями
- [ ] Factories создают сложные объекты
- [ ] Use cases не создаются inline

### Infrastructure Layer
- [ ] Репозитории конвертируют Model ↔ Entity
- [ ] Framework-исключения конвертируются в доменные
- [ ] Порты реализованы корректно

### Presentation Layer
- [ ] DI через Depends
- [ ] Handlers только делегируют
- [ ] DTOs для Request/Response
