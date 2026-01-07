from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from domain.entities.user import User
from domain.interfaces.user_repository_port import UserRepositoryPort


@dataclass(slots=True)
class UpdateUserFlagsUseCase:
    """Use case для обновления флагов пользователя (is_active, is_verified)."""

    user_repository: UserRepositoryPort

    async def execute(
        self,
        user_id: UUID,
        *,
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise ValueError(f"Пользователь с ID {user_id} не найден")

        if is_active is not None:
            user.is_active = is_active
        if is_verified is not None:
            user.is_verified = is_verified

        return await self.user_repository.update(user)

