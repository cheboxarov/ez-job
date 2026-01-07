from __future__ import annotations

from dataclasses import dataclass

from domain.entities.user import User
from domain.interfaces.user_repository_port import UserRepositoryPort


@dataclass(slots=True)
class ListUsersForAdminUseCase:
    """Use case для получения списка пользователей для админки."""

    user_repository: UserRepositoryPort

    async def execute(
        self,
        phone_substring: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[User], int]:
        return await self.user_repository.search_for_admin(
            phone_substring=phone_substring,
            page=page,
            page_size=page_size,
        )

