from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from domain.interfaces.resume_repository_port import ResumeRepositoryPort
from domain.interfaces.telegram_link_token_repository_port import (
    TelegramLinkTokenRepositoryPort,
)
from domain.interfaces.telegram_notification_settings_repository_port import (
    TelegramNotificationSettingsRepositoryPort,
)
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from domain.interfaces.user_repository_port import UserRepositoryPort
from domain.interfaces.user_subscription_repository_port import (
    UserSubscriptionRepositoryPort,
)


@dataclass(slots=True)
class DeleteUserCascadeUseCase:
    """Use case для каскадного удаления пользователя и связанных данных.

    Часть связей уже покрывается ondelete=CASCADE на уровне БД (user_subscriptions, llm_calls и др.),
    здесь мы явно чистим только то, для чего есть доменные операции.
    """

    unit_of_work: UnitOfWorkPort

    @property
    def user_repository(self) -> UserRepositoryPort:
        return self.unit_of_work.user_repository

    @property
    def user_subscription_repository(self) -> UserSubscriptionRepositoryPort:
        return self.unit_of_work.user_subscription_repository

    @property
    def resume_repository(self) -> ResumeRepositoryPort:
        return self.unit_of_work.resume_repository

    @property
    def telegram_notification_settings_repository(
        self,
    ) -> TelegramNotificationSettingsRepositoryPort:
        return self.unit_of_work.telegram_notification_settings_repository

    @property
    def telegram_link_token_repository(self) -> TelegramLinkTokenRepositoryPort:
        return self.unit_of_work.telegram_link_token_repository

    async def execute(self, user_id: UUID) -> None:
        # Все операции выполняем в рамках одного UnitOfWork/транзакции
        async with self.unit_of_work:
            # Удаляем резюме пользователя
            resumes = await self.resume_repository.list_by_user_id(user_id)
            for resume in resumes:
                await self.resume_repository.delete(resume.id)

            # Удаляем настройки уведомлений и токены Telegram
            await self.telegram_notification_settings_repository.delete(user_id)
            await self.telegram_link_token_repository.delete_by_user_id(user_id)

            # Подписка и зависящие от пользователя записи с CASCADE должны быть очищены на уровне БД

            # Удаляем пользователя
            await self.user_repository.delete(user_id)

            await self.unit_of_work.commit()

