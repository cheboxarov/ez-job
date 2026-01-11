"""Агент для проверки patch-операций на соответствие правилам."""

from __future__ import annotations

from typing import List
from uuid import UUID

from config import OpenAIConfig
from domain.entities.resume_edit_patch import ResumeEditPatch
from infrastructure.agents.base_agent import BaseAgent
from infrastructure.agents.resume_edit.tools.rule_check_tool import check_all_rules
from infrastructure.agents.resume_edit.tools.validate_patch_tool import validate_patches


class ResumeEditReviewerAgent(BaseAgent):
    """Агент для проверки patch-операций на соответствие правилам HH.ru."""

    AGENT_NAME = "ResumeEditReviewerAgent"

    async def review_patches(
        self,
        resume_text: str,
        patches: List[ResumeEditPatch],
        user_id: UUID | None = None,
    ) -> tuple[List[ResumeEditPatch], List[str]]:
        """Проверить patch-операции на соответствие правилам.

        Args:
            resume_text: Текст резюме.
            patches: Список patch-операций для проверки.
            user_id: ID пользователя.

        Returns:
            Кортеж (validated_patches, warnings).
        """
        warnings: List[str] = []

        # Валидация через инструмент
        is_valid, errors = validate_patches(patches, resume_text)
        if not is_valid:
            warnings.extend(errors)

        # Проверка правил для нового текста
        for patch in patches:
            if patch.new_text:
                # Проверяем новый текст на соответствие правилам
                rules_check = check_all_rules(patch.new_text)
                if rules_check["issues"]:
                    warnings.append(
                        f"Patch {patch.id}: найдены проблемы в новом тексте: "
                        f"{', '.join(rules_check['issues'][:3])}"
                    )

        # Проверка на длинное тире в новом тексте
        for patch in patches:
            if patch.new_text and "—" in patch.new_text:
                warnings.append(
                    f"Patch {patch.id}: найдено длинное тире (—) в новом тексте - замени на дефис (-)"
                )

        # Проверка на шаблонные формулировки
        template_phrases = [
            "разработал реферальную систему",
            "модуль квестов",
            "партнерскую интеграцию",
        ]
        for patch in patches:
            if patch.new_text:
                for phrase in template_phrases:
                    if phrase.lower() in patch.new_text.lower():
                        warnings.append(
                            f"Patch {patch.id}: найдена шаблонная формулировка: {phrase}"
                        )

        return (patches, warnings)
