"""Утилита для формирования текстового контента резюме из данных HeadHunter."""

from __future__ import annotations

from domain.entities.hh_resume_detailed import HHResumeDetailed


def format_hh_resume_to_content(hh_resume: HHResumeDetailed) -> str:
    """Формирует структурированный текстовый контент из детального резюме HeadHunter.

    Создает читаемый текст, содержащий всю информацию резюме для подбора вакансий.

    Args:
        hh_resume: Детальное резюме из HeadHunter.

    Returns:
        Отформатированный текстовый контент резюме.
    """
    parts: list[str] = []

    # Имя, фамилия, отчество
    name_parts = []
    if hh_resume.last_name:
        name_parts.append(hh_resume.last_name)
    if hh_resume.first_name:
        name_parts.append(hh_resume.first_name)
    if hh_resume.middle_name:
        name_parts.append(hh_resume.middle_name)
    if name_parts:
        parts.append(" ".join(name_parts))
        parts.append("")  # Пустая строка для разделения

    # Название резюме (должность)
    if hh_resume.title:
        parts.append(hh_resume.title)
        parts.append("")

    # Регион
    if hh_resume.area_name:
        parts.append(f"Регион: {hh_resume.area_name}")

    # Зарплата
    if hh_resume.salary_amount is not None:
        salary_str = f"Зарплата: {hh_resume.salary_amount}"
        if hh_resume.salary_currency:
            salary_str += f" {hh_resume.salary_currency}"
        parts.append(salary_str)

    # Навыки
    if hh_resume.key_skills:
        skills_str = ", ".join(hh_resume.key_skills)
        parts.append("")
        parts.append(f"Навыки: {skills_str}")

    # Опыт работы
    if hh_resume.work_experience:
        parts.append("")
        parts.append("Опыт работы:")
        for exp in hh_resume.work_experience:
            parts.append("")
            # Компания и должность
            exp_header = f"{exp.company_name}"
            if exp.position:
                exp_header += f" - {exp.position}"
            parts.append(exp_header)

            # Даты
            date_range = []
            if exp.start_date:
                date_range.append(exp.start_date)
            if exp.end_date:
                date_range.append(exp.end_date)
            elif not exp.start_date:
                date_range.append("настоящее время")

            if date_range:
                parts.append(" - ".join(date_range))

            # Длительность
            if exp.duration_years is not None or exp.duration_months is not None:
                duration_parts = []
                if exp.duration_years is not None and exp.duration_years > 0:
                    if exp.duration_years == 1:
                        duration_parts.append("1 год")
                    elif exp.duration_years < 5:
                        duration_parts.append(f"{exp.duration_years} года")
                    else:
                        duration_parts.append(f"{exp.duration_years} лет")
                if exp.duration_months is not None and exp.duration_months > 0:
                    if exp.duration_months == 1:
                        duration_parts.append("1 месяц")
                    elif exp.duration_months < 5:
                        duration_parts.append(f"{exp.duration_months} месяца")
                    else:
                        duration_parts.append(f"{exp.duration_months} месяцев")
                if duration_parts:
                    parts.append(f"({', '.join(duration_parts)})")

            # Описание
            if exp.description:
                parts.append("")
                parts.append(exp.description)

    # О себе
    if hh_resume.about:
        parts.append("")
        parts.append("О себе:")
        parts.append(hh_resume.about)

    return "\n".join(parts)

