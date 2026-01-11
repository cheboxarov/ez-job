import pytest

from config import OpenAIConfig
from infrastructure.agents.resume_edit.tools import deepagents_patch_tool
from infrastructure.agents.resume_edit.tools import deepagents_question_tool


@pytest.mark.asyncio
async def test_generate_patches_tool(monkeypatch):
    async def fake_call_llm(self, *args, **kwargs):
        return {
            "action": "generate_patches",
            "assistant_message": "Обновил описание роли.",
            "patches": [
                {
                    "type": "replace",
                    "start_line": 2,
                    "end_line": 2,
                    "old_text": "Разработчик Python",
                    "new_text": "Python разработчик",
                    "reason": "Уточнение роли",
                }
            ],
        }

    monkeypatch.setattr(
        deepagents_patch_tool._PatchToolAgent,
        "_call_llm_with_retry",
        fake_call_llm,
    )

    tool = deepagents_patch_tool.create_deepagents_patch_tool(
        OpenAIConfig(api_key="test")
    )
    resume_text = "Опыт работы\nРазработчик Python\n- Делал вещи"
    result = await tool.ainvoke(
        {
            "resume_text": resume_text,
            "user_message": "Уточни название роли",
            "current_task": {"id": "1", "title": "Правки роли", "status": "in_progress"},
            "history": [],
        }
    )

    assert result["action"] == "generate_patches"
    assert result["patches"]
    assert result["patches"][0]["new_text"] == "Python разработчик"
    assert "questions" in result
    assert "warnings" in result


@pytest.mark.asyncio
async def test_generate_questions_tool(monkeypatch):
    async def fake_call_llm(self, *args, **kwargs):
        return {
            "action": "ask_question",
            "assistant_message": "Нужно уточнить детали.",
            "questions": [
                {
                    "id": "9a5a4a2a-5b48-4b98-9d86-1f8d8f5f0d3a",
                    "text": "Какой стек использовали?",
                    "required": True,
                    "suggested_answers": ["Python", "Go", "не знаю, придумай сам"],
                    "allow_multiple": True,
                }
            ],
        }

    monkeypatch.setattr(
        deepagents_question_tool._QuestionToolAgent,
        "_call_llm_with_retry",
        fake_call_llm,
    )

    tool = deepagents_question_tool.create_deepagents_question_tool(
        OpenAIConfig(api_key="test")
    )
    resume_text = "Опыт работы\nРазработчик Python\n- Делал вещи"
    result = await tool.ainvoke(
        {
            "resume_text": resume_text,
            "user_message": "Уточни стек",
            "current_task": {"id": "1", "title": "Вопросы", "status": "in_progress"},
            "history": [],
        }
    )

    assert result["action"] == "ask_question"
    assert result["questions"]
    assert result["questions"][0]["text"] == "Какой стек использовали?"
    assert "patches" in result
    assert "warnings" in result
