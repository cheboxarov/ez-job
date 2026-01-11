"""Инструмент для генерации patch-операций."""

from __future__ import annotations

from typing import Dict, List
from uuid import uuid4

from domain.entities.resume_edit_patch import ResumeEditPatch
from loguru import logger


def lines_to_positions(resume_text: str, start_line: int, end_line: int) -> tuple[int, int] | None:
    """Преобразовать номера строк в позиции в тексте.

    Args:
        resume_text: Текст резюме.
        start_line: Номер начальной строки (0-based).
        end_line: Номер конечной строки (0-based).

    Returns:
        Кортеж (start_pos, end_pos) или None, если строки не найдены.
    """
    lines = resume_text.splitlines(keepends=True)

    if start_line < 0 or end_line >= len(lines) or start_line > end_line:
        return None

    start_pos = sum(len(lines[i]) for i in range(start_line))
    end_pos = start_pos + sum(len(lines[i]) for i in range(start_line, end_line + 1))

    return (start_pos, end_pos)


def positions_to_lines(resume_text: str, start_pos: int, end_pos: int) -> tuple[int, int] | None:
    """Преобразовать позиции в тексте в номера строк (0-based).

    Args:
        resume_text: Текст резюме.
        start_pos: Позиция начала.
        end_pos: Позиция конца (exclusive).

    Returns:
        Кортеж (start_line, end_line) или None, если позиции некорректны.
    """
    if start_pos < 0 or end_pos < 0 or end_pos < start_pos:
        return None

    lines = resume_text.splitlines(keepends=True)
    if not lines:
        return None

    start_line = None
    end_line = None
    cursor = 0
    for idx, line in enumerate(lines):
        line_end = cursor + len(line)
        if start_line is None and start_pos < line_end:
            start_line = idx
        if end_pos <= line_end:
            end_line = idx
            break
        cursor = line_end

    if start_line is None or end_line is None:
        return None

    return (start_line, end_line)


def build_patch(
    resume_text: str,
    patch_type: str,
    old_text: str,
    new_text: str | None = None,
    start_line: int | None = None,
    end_line: int | None = None,
    reason: str = "",
) -> ResumeEditPatch | None:
    """Построить patch-операцию на основе номеров строк.

    Args:
        resume_text: Текст резюме.
        patch_type: Тип операции ("replace", "insert", "delete").
        old_text: Старый текст (для replace/delete). Для insert может быть пустой строкой.
        new_text: Новый текст (None для delete).
        start_line: Номер начальной строки (1-based от LLM).
        end_line: Номер конечной строки (1-based от LLM).
        reason: Объяснение изменения.

    Returns:
        ResumeEditPatch или None, если не удалось построить.
    """
    if patch_type not in ["replace", "insert", "delete"]:
        return None

    if patch_type == "delete" and new_text is not None:
        return None

    if patch_type in ["replace", "insert"] and new_text is None:
        return None

    # Проверяем, что номера строк указаны
    if start_line is None or end_line is None:
        logger.warning(
            f"build_patch: не указаны номера строк. "
            f"type: {patch_type}, start_line: {start_line}, end_line: {end_line}"
        )
        return None

    # Конвертируем из 1-based (от LLM) в 0-based (для внутренней обработки)
    start_line_0based = start_line - 1
    end_line_0based = end_line - 1

    # Проверяем валидность номеров строк
    lines = resume_text.splitlines()
    if start_line_0based < 0 or end_line_0based >= len(lines) or start_line_0based > end_line_0based:
        logger.warning(
            f"build_patch: некорректные номера строк. "
            f"type: {patch_type}, start_line: {start_line} (0-based: {start_line_0based}), "
            f"end_line: {end_line} (0-based: {end_line_0based}), "
            f"total_lines: {len(lines)}"
        )
        return None

    # Для insert: вставляем после указанной строки
    if patch_type == "insert":
        # Для insert end_line должен быть равен start_line (вставляем после одной строки)
        # Но мы используем start_line как позицию вставки
        final_start_line = start_line  # 1-based для патча
        final_end_line = start_line   # 1-based для патча
    else:
        # Для replace и delete используем указанный диапазон
        final_start_line = start_line  # 1-based для патча
        final_end_line = end_line      # 1-based для патча

    # Генерируем ID
    patch_id = str(uuid4())

    return ResumeEditPatch(
        id=patch_id,
        type=patch_type,  # type: ignore
        start_line=final_start_line,
        end_line=final_end_line,
        old_text=old_text,
        new_text=new_text,
        reason=reason,
    )


def build_patches_from_changes(
    resume_text: str,
    changes: List[Dict[str, any]],
) -> List[ResumeEditPatch]:
    """Построить список patch-операций из списка изменений.

    Args:
        resume_text: Текст резюме.
        changes: Список изменений в формате:
            [{"type": "replace", "old_text": "...", "new_text": "...", "start_line": 1, "end_line": 2, "reason": "..."}, ...]

    Returns:
        Список ResumeEditPatch.
    """
    patches: List[ResumeEditPatch] = []

    logger.debug(
        f"build_patches_from_changes: начинаю построение {len(changes)} патчей из данных"
    )

    for idx, change in enumerate(changes):
        patch = build_patch(
            resume_text=resume_text,
            patch_type=change.get("type", "replace"),
            old_text=change.get("old_text", ""),
            new_text=change.get("new_text"),
            start_line=change.get("start_line"),
            end_line=change.get("end_line"),
            reason=change.get("reason", ""),
        )

        if patch:
            patches.append(patch)
            logger.debug(
                f"build_patches_from_changes: успешно построен патч #{idx + 1}: "
                f"type={patch.type}, start_line={patch.start_line}, end_line={patch.end_line}"
            )
        else:
            logger.warning(
                f"build_patches_from_changes: не удалось построить патч #{idx + 1}. "
                f"Данные: type={change.get('type')}, "
                f"start_line={change.get('start_line')}, end_line={change.get('end_line')}, "
                f"old_text={change.get('old_text', '')[:50] if change.get('old_text') else 'None'}..."
            )

    logger.info(
        f"build_patches_from_changes: построено {len(patches)} из {len(changes)} патчей"
    )

    return patches
