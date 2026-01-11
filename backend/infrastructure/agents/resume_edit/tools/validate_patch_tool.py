"""Инструмент для валидации patch-операций."""

from __future__ import annotations

from typing import List

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from domain.entities.resume_edit_patch import ResumeEditPatch


def validate_patch(
    patch: ResumeEditPatch, resume_text: str, max_changed_lines_percent: float = 25.0
) -> tuple[bool, str | None]:
    """Валидировать одну patch-операцию.

    Args:
        patch: Patch-операция для валидации.
        resume_text: Текст резюме.
        max_changed_lines_percent: Максимальный процент измененных строк.

    Returns:
        Кортеж (is_valid, error_message).
    """
    # Проверка типа операции
    if patch.type not in ["replace", "insert", "delete"]:
        return (False, f"Неизвестный тип операции: {patch.type}")

    # Для replace/delete old_text обязателен, для insert может быть пустым
    if patch.type in ["replace", "delete"] and not patch.old_text:
        return (False, "old_text не может быть пустым для replace/delete")

    # Проверка new_text для replace и insert (допускаем пустую строку, но не None)
    if patch.type in ["replace", "insert"] and patch.new_text is None:
        return (False, f"new_text обязателен для операции {patch.type}")

    # Проверка new_text для delete
    if patch.type == "delete" and patch.new_text is not None:
        return (False, "new_text должен быть None для операции delete")

    # Проверка номеров строк (обязательны)
    if patch.start_line is None or patch.end_line is None:
        return (False, "start_line и end_line обязательны для всех типов патчей")

    # Проверка валидности номеров строк
    lines = resume_text.splitlines()
    total_lines = len(lines)
    
    # Конвертируем из 1-based в 0-based для проверки
    start_line_0based = patch.start_line - 1
    end_line_0based = patch.end_line - 1
    
    if start_line_0based < 0 or end_line_0based >= total_lines:
        return (
            False,
            f"Номера строк вне диапазона: start_line={patch.start_line}, end_line={patch.end_line}, "
            f"всего строк={total_lines}"
        )
    
    if start_line_0based > end_line_0based:
        return (
            False,
            f"start_line ({patch.start_line}) не может быть больше end_line ({patch.end_line})"
        )

    # Проверка применимости к тексту (проверяем, что old_text соответствует указанным строкам)
    if patch.type in ["replace", "delete"]:
        # Извлекаем текст из указанных строк
        actual_text = "\n".join(lines[start_line_0based : end_line_0based + 1])
        
        # Сравниваем с old_text (нормализуем пробелы в конце строк)
        # Убираем лишние пробелы в конце каждой строки для сравнения
        actual_text_normalized = "\n".join(line.rstrip() for line in actual_text.splitlines())
        old_text_normalized = "\n".join(line.rstrip() for line in patch.old_text.splitlines())
        
        if actual_text_normalized != old_text_normalized:
            return (
                False,
                f"old_text не соответствует тексту в строках {patch.start_line}-{patch.end_line}. "
                f"Ожидалось: {actual_text_normalized[:100]}..., получено: {old_text_normalized[:100]}..."
            )

    # Проверка лимитов на строки
    if total_lines == 0:
        return (True, None)

    # Для insert считаем только новые строки, для replace/delete - измененные строки
    if patch.type == "insert":
        # Для insert считаем количество новых строк
        new_lines_count = len(patch.new_text.splitlines()) if patch.new_text else 0
        changed_lines_percent = (new_lines_count / total_lines) * 100 if total_lines > 0 else 0
    else:
        # Для replace и delete считаем количество измененных строк
        changed_lines = patch.end_line - patch.start_line + 1
        changed_lines_percent = (changed_lines / total_lines) * 100

    if changed_lines_percent > max_changed_lines_percent:
        return (
            False,
            f"Изменено {changed_lines_percent:.1f}% строк (максимум {max_changed_lines_percent}%)",
        )

    return (True, None)


def validate_patches(
    patches: List[ResumeEditPatch],
    resume_text: str,
    max_changed_lines_percent: float = 25.0,
    max_patch_items: int = 12,
) -> tuple[bool, List[str]]:
    """Валидировать список patch-операций.

    Args:
        patches: Список patch-операций.
        resume_text: Текст резюме.
        max_changed_lines_percent: Максимальный процент измененных строк.
        max_patch_items: Максимальное количество patch-операций.

    Returns:
        Кортеж (is_valid, list_of_errors).
    """
    errors: List[str] = []

    # Проверка количества patch
    if len(patches) > max_patch_items:
        errors.append(
            f"Слишком много patch-операций: {len(patches)} (максимум {max_patch_items})"
        )

    # Проверка каждой patch
    for i, patch in enumerate(patches):
        is_valid, error = validate_patch(patch, resume_text, max_changed_lines_percent)
        if not is_valid:
            errors.append(f"Patch #{i + 1}: {error}")

    # Проверка общего процента измененных строк
    total_lines = len(resume_text.splitlines())
    if total_lines > 0:
        changed_lines = set()
        for patch in patches:
            # Для insert считаем новые строки, для replace/delete - измененные строки
            if patch.type == "insert":
                # Для insert добавляем строки после start_line (новые строки)
                new_lines_count = len(patch.new_text.splitlines()) if patch.new_text else 0
                for i in range(new_lines_count):
                    changed_lines.add(patch.start_line + i + 1)  # +1 потому что вставляем после start_line
            else:
                # Для replace и delete считаем измененные строки
                for line_num in range(patch.start_line, patch.end_line + 1):
                    changed_lines.add(line_num)

        changed_lines_percent = (len(changed_lines) / total_lines) * 100
        if changed_lines_percent > max_changed_lines_percent:
            errors.append(
                f"Общий процент измененных строк: {changed_lines_percent:.1f}% "
                f"(максимум {max_changed_lines_percent}%)"
            )

    # Проверка на конфликты (пересекающиеся диапазоны)
    for i, patch1 in enumerate(patches):
        for j, patch2 in enumerate(patches[i + 1 :], start=i + 1):
            # Для insert проверяем, что вставка не пересекается с другими операциями
            if patch1.type == "insert":
                # Insert вставляет после start_line, проверяем пересечение
                if patch2.type == "insert":
                    # Два insert не могут быть на одной строке
                    if patch1.start_line == patch2.start_line:
                        errors.append(
                            f"Конфликт между patch #{i + 1} и #{j + 1}: "
                            f"оба insert на строке {patch1.start_line}"
                        )
                else:
                    # Insert не должен пересекаться с replace/delete
                    if patch2.start_line <= patch1.start_line <= patch2.end_line:
                        errors.append(
                            f"Конфликт между patch #{i + 1} (insert) и #{j + 1} ({patch2.type}): "
                            f"вставка на строке {patch1.start_line} пересекается с диапазоном {patch2.start_line}-{patch2.end_line}"
                        )
            elif patch2.type == "insert":
                # Аналогично для второго патча
                if patch1.start_line <= patch2.start_line <= patch1.end_line:
                    errors.append(
                        f"Конфликт между patch #{i + 1} ({patch1.type}) и #{j + 1} (insert): "
                        f"вставка на строке {patch2.start_line} пересекается с диапазоном {patch1.start_line}-{patch1.end_line}"
                    )
            else:
                # Оба патча - replace или delete, проверяем пересечение диапазонов
                if not (
                    patch1.end_line < patch2.start_line
                    or patch2.end_line < patch1.start_line
                ):
                    errors.append(
                        f"Конфликт между patch #{i + 1} и #{j + 1}: "
                        f"пересекающиеся диапазоны строк ({patch1.start_line}-{patch1.end_line} и {patch2.start_line}-{patch2.end_line})"
                    )

    return (len(errors) == 0, errors)


class ValidatePatchesInput(BaseModel):
    """Входные данные для валидации патчей."""

    resume_text: str = Field(..., description="Текст резюме.")
    patches: List[dict] = Field(..., description="Список патчей в формате JSON.")
    max_changed_lines_percent: float = Field(
        default=25.0, description="Максимальный процент измененных строк."
    )
    max_patch_items: int = Field(default=12, description="Максимальное количество патчей.")


@tool("validate_resume_patches", args_schema=ValidatePatchesInput)
def validate_resume_patches_tool(
    resume_text: str,
    patches: List[dict],
    max_changed_lines_percent: float = 25.0,
    max_patch_items: int = 12,
) -> dict:
    """Валидировать патчи редактирования резюме."""
    patch_objects: List[ResumeEditPatch] = []
    errors: List[str] = []

    for idx, patch_data in enumerate(patches):
        try:
            patch_objects.append(
                ResumeEditPatch(
                    id=patch_data.get("id"),
                    type=patch_data.get("type", "replace"),  # type: ignore
                    old_text=patch_data.get("old_text", ""),
                    new_text=patch_data.get("new_text"),
                    reason=patch_data.get("reason", ""),
                    start_line=patch_data.get("start_line"),
                    end_line=patch_data.get("end_line"),
                )
            )
        except Exception as exc:
            errors.append(f"Patch #{idx + 1}: ошибка преобразования ({exc})")

    if errors:
        return {"is_valid": False, "errors": errors}

    is_valid, validation_errors = validate_patches(
        patches=patch_objects,
        resume_text=resume_text,
        max_changed_lines_percent=max_changed_lines_percent,
        max_patch_items=max_patch_items,
    )
    return {"is_valid": is_valid, "errors": validation_errors}
