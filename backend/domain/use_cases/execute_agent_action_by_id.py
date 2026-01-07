"""Use case для выполнения AgentAction по ID."""

from __future__ import annotations

from typing import Dict
from uuid import UUID

from loguru import logger

from domain.entities.agent_action import AgentAction
from domain.interfaces.agent_action_repository_port import AgentActionRepositoryPort
from domain.use_cases.execute_agent_action import ExecuteAgentActionUseCase
from domain.use_cases.mark_agent_action_as_sent import MarkAgentActionAsSentUseCase
from domain.use_cases.update_user_hh_auth_cookies import UpdateUserHhAuthCookiesUseCase


class ExecuteAgentActionByIdUseCase:
    """Use case для выполнения AgentAction по ID.

    Получает AgentAction по ID, проверяет права доступа и тип действия,
    выполняет действие и помечает его как отправленное при успехе.
    """

    def __init__(
        self,
        agent_action_repository: AgentActionRepositoryPort,
        execute_agent_action_uc: ExecuteAgentActionUseCase,
        mark_agent_action_as_sent_uc: MarkAgentActionAsSentUseCase,
    ) -> None:
        """Инициализация use case.

        Args:
            agent_action_repository: Репозиторий для работы с действиями агента.
            execute_agent_action_uc: Use case для выполнения действия агента.
            mark_agent_action_as_sent_uc: Use case для пометки действия как отправленного.
        """
        self._agent_action_repository = agent_action_repository
        self._execute_agent_action_uc = execute_agent_action_uc
        self._mark_agent_action_as_sent_uc = mark_agent_action_as_sent_uc

    async def execute(
        self,
        action_id: UUID,
        user_id: UUID,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        update_cookies_uc: UpdateUserHhAuthCookiesUseCase,
    ) -> AgentAction:
        """Выполнить AgentAction по ID.

        Args:
            action_id: UUID действия агента.
            user_id: UUID пользователя (для проверки прав доступа).
            headers: HTTP заголовки для запросов к HH API.
            cookies: HTTP cookies для запросов к HH API.
            update_cookies_uc: Use case для обновления cookies.

        Returns:
            Обновленная доменная сущность AgentAction с data["sended"] = True.

        Raises:
            ValueError: Если действие не найдено, не принадлежит пользователю,
                       не является типом send_message или уже отправлено.
            Exception: При ошибках выполнения действия.
        """
        # Получаем действие из репозитория
        action = await self._agent_action_repository.get_by_id(action_id)

        if action is None:
            raise ValueError(f"Действие с ID {action_id} не найдено")

        # Проверяем права доступа
        if action.user_id != user_id:
            raise ValueError(f"Действие {action_id} не принадлежит пользователю {user_id}")

        # Проверяем тип действия
        if action.type != "send_message":
            raise ValueError(f"Действие {action_id} не является типом send_message")

        # Проверяем, не отправлено ли уже
        if action.data.get("sended") is True:
            raise ValueError(f"Действие {action_id} уже отправлено")

        # Выполняем действие
        logger.info(f"Выполнение действия {action_id} для пользователя {user_id}")
        await self._execute_agent_action_uc.execute(
            action=action,
            headers=headers,
            cookies=cookies,
            user_id=user_id,
            update_cookies_uc=update_cookies_uc,
        )

        # Помечаем как отправленное
        updated_action = await self._mark_agent_action_as_sent_uc.execute(action)

        logger.info(f"Действие {action_id} успешно выполнено и помечено как отправленное")

        return updated_action
