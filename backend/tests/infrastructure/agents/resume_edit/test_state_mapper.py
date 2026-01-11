from infrastructure.agents.resume_edit.deepagents.state_mapper import (
    state_to_resume_edit_result,
)


def test_state_to_resume_edit_result_with_structured_response():
    state = {
        "structured_response": {
            "action": "generate_patches",
            "assistant_message": "Готово.",
            "patches": [
                {
                    "id": "p1",
                    "type": "replace",
                    "start_line": 1,
                    "end_line": 1,
                    "old_text": "A",
                    "new_text": "B",
                    "reason": "Обновление",
                }
            ],
            "questions": [
                {
                    "id": "9a5a4a2a-5b48-4b98-9d86-1f8d8f5f0d3a",
                    "text": "Уточнить деталь?",
                    "required": True,
                    "suggested_answers": ["да", "нет"],
                    "allow_multiple": False,
                }
            ],
            "warnings": ["Проверьте изменения"],
        },
        "todos": [{"content": "Шаг 1", "status": "in_progress"}],
    }

    result = state_to_resume_edit_result(state)
    assert result.assistant_message == "Готово."
    assert len(result.patches) == 1
    assert len(result.questions) == 1
    assert result.warnings == ["Проверьте изменения"]
    assert result.plan and result.plan[0]["status"] == "in_progress"
