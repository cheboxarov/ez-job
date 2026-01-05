# Добавление новых фич

Пошаговое руководство по разработке новых фич в проекте "AutoOffer".

## Процесс разработки

### 1. Планирование

1. Определите требования к фиче
2. Определите, какие сущности нужны
3. Определите, какие Use Cases нужны
4. Спланируйте изменения в БД (если нужны)

### 2. Создание ветки

```bash
git checkout -b feature/your-feature-name
```

### 3. Разработка по слоям

Следуйте порядку разработки согласно Clean Architecture:

#### Шаг 1: Domain слой

**Определите сущности (если нужны):**

```python
# domain/entities/your_entity.py
@dataclass(slots=True)
class YourEntity:
    id: UUID
    name: str
    # ...
```

**Определите интерфейсы:**

```python
# domain/interfaces/your_repository_port.py
class YourRepositoryPort(ABC):
    @abstractmethod
    async def create(self, entity: YourEntity) -> YourEntity:
        pass
```

**Создайте Use Cases:**

```python
# domain/use_cases/create_your_entity.py
class CreateYourEntityUseCase:
    def __init__(self, repository: YourRepositoryPort):
        self._repository = repository
    
    async def execute(self, name: str) -> YourEntity:
        entity = YourEntity(id=uuid4(), name=name)
        return await self._repository.create(entity)
```

#### Шаг 2: Infrastructure слой

**Реализуйте интерфейсы:**

```python
# infrastructure/database/repositories/your_repository.py
class YourRepository(YourRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, entity: YourEntity) -> YourEntity:
        model = YourEntityModel.from_entity(entity)
        self._session.add(model)
        await self._session.flush()
        return model.to_entity()
```

**Создайте модель БД:**

```python
# infrastructure/database/models/your_entity_model.py
class YourEntityModel(Base):
    __tablename__ = "your_entities"
    # ...
```

**Создайте миграцию:**

```bash
cd backend
alembic revision --autogenerate -m "create_your_entities_table"
```

#### Шаг 3: Application слой (если нужна оркестрация)

```python
# application/services/your_service.py
class YourService:
    def __init__(self, unit_of_work: UnitOfWorkPort):
        self._unit_of_work = unit_of_work
    
    async def create_with_validation(self, name: str):
        async with self._unit_of_work:
            use_case = CreateYourEntityUseCase(
                self._unit_of_work.your_repository
            )
            entity = await use_case.execute(name)
            await self._unit_of_work.commit()
            return entity
```

#### Шаг 4: Presentation слой

**Создайте DTO:**

```python
# presentation/dto/your_request.py
class CreateYourEntityRequest(BaseModel):
    name: str

# presentation/dto/your_response.py
class YourEntityResponse(BaseModel):
    id: UUID
    name: str
```

**Создайте роутер:**

```python
# presentation/routers/your_router.py
router = APIRouter(prefix="/api/your", tags=["your"])

@router.post("", response_model=YourEntityResponse)
async def create_entity(
    request: CreateYourEntityRequest,
    current_user: UserModel = Depends(get_current_active_user),
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
):
    use_case = CreateYourEntityUseCase(
        unit_of_work.your_repository
    )
    entity = await use_case.execute(request.name)
    return YourEntityResponse.from_entity(entity)
```

**Подключите роутер:**

```python
# presentation/app.py
from presentation.routers.your_router import router as your_router
app.include_router(your_router)
```

### 4. Тестирование

Напишите тесты для новой функциональности:

```python
# tests/test_your_feature.py
async def test_create_entity():
    # Тест Use Case
    pass
```

### 5. Code Review

1. Создайте Pull Request
2. Дождитесь code review
3. Внесите исправления при необходимости

### 6. Мерж

После одобрения PR, выполните мерж в main.

## Примеры

### Добавление нового эндпоинта

См. процесс выше, шаги 1-4.

### Добавление новой сущности

1. Создайте Entity в Domain
2. Создайте Interface в Domain
3. Создайте Model в Infrastructure
4. Создайте Repository в Infrastructure
5. Добавьте в UnitOfWork
6. Создайте миграцию

### Добавление нового Use Case

1. Определите зависимости (интерфейсы)
2. Реализуйте бизнес-логику
3. Используйте в роутерах или сервисах

## Чеклист для новой фичи

- [ ] Создана ветка для фичи
- [ ] Определены сущности (если нужны)
- [ ] Созданы интерфейсы в Domain
- [ ] Реализованы интерфейсы в Infrastructure
- [ ] Созданы Use Cases
- [ ] Созданы DTO и роутеры
- [ ] Созданы/обновлены миграции БД
- [ ] Написаны тесты
- [ ] Код соответствует стилю проекта
- [ ] Обновлена документация (если нужно)
- [ ] Создан Pull Request

## Связанные разделы

- [Архитектура](../architecture/layers.md) — описание слоев
- [Стиль кода](code-style.md) — стандарты кодирования
