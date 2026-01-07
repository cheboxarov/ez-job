"""Сервис приложения для админских операций с пользователями."""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from domain.entities.user import User
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.use_cases.admin.get_user_detail_for_admin import GetUserDetailForAdminUseCase
from domain.use_cases.admin.list_users_for_admin import ListUsersForAdminUseCase
from domain.use_cases.admin.update_user_flags import UpdateUserFlagsUseCase
from domain.use_cases.change_user_subscription import ChangeUserSubscriptionUseCase
from domain.use_cases.admin.delete_user_cascade import DeleteUserCascadeUseCase


class AdminUserService:
    """Сервис, оркестрирующий админские use case-ы по пользователям.

    Хендлеры FastAPI должны вызывать методы этого сервиса, не трогая репозитории
    и use case-ы напрямую.
    """

    def __init__(self, unit_of_work: UnitOfWorkPort) -> None:
        self._unit_of_work = unit_of_work

    async def list_users(
        self,
        *,
        phone_substring: str | None,
        page: int,
        page_size: int,
    ) -> tuple[Sequence[User], int]:
        """Получить список пользователей для админки."""
        async with self._unit_of_work:
            use_case = ListUsersForAdminUseCase(
                user_repository=self._unit_of_work.user_repository,
            )
            return await use_case.execute(
                phone_substring=phone_substring,
                page=page,
                page_size=page_size,
            )

    async def get_user_detail(
        self,
        user_id: UUID,
    ):
        """Получить детальную информацию по пользователю."""
        async with self._unit_of_work:
            use_case = GetUserDetailForAdminUseCase(
                user_repository=self._unit_of_work.user_repository,
                user_subscription_repository=self._unit_of_work.user_subscription_repository,
                subscription_plan_repository=self._unit_of_work.subscription_plan_repository,
            )
            return await use_case.execute(user_id=user_id)

    async def update_user_flags(
        self,
        user_id: UUID,
        *,
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ) -> User:
        """Обновить флаги пользователя."""
        async with self._unit_of_work:
            use_case = UpdateUserFlagsUseCase(
                user_repository=self._unit_of_work.user_repository,
            )
            user = await use_case.execute(
                user_id=user_id,
                is_active=is_active,
                is_verified=is_verified,
            )
            await self._unit_of_work.commit()
            return user

    async def change_user_subscription(
        self,
        user_id: UUID,
        plan_name: str,
    ):
        """Сменить тарифный план пользователя."""
        async with self._unit_of_work:
            use_case = ChangeUserSubscriptionUseCase(
                user_subscription_repository=self._unit_of_work.user_subscription_repository,
                subscription_plan_repository=self._unit_of_work.subscription_plan_repository,
            )
            result = await use_case.execute(user_id=user_id, plan_name=plan_name)
            await self._unit_of_work.commit()
            return result

    async def delete_user(self, user_id: UUID) -> None:
        """Каскадно удалить пользователя и связанные данные."""
        use_case = DeleteUserCascadeUseCase(unit_of_work=self._unit_of_work)
        await use_case.execute(user_id=user_id)

