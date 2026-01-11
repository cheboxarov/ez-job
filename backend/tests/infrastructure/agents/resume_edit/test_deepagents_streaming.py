import pytest

from langchain_core.messages import AIMessage

from infrastructure.agents.resume_edit.deepagents.streaming_adapter import stream_deep_agent
from infrastructure.agents.resume_edit.deepagents.state_mapper import todos_to_plan


class FakeAgent:
    def __init__(self, states):
        self._states = states

    async def astream(self, input_data, stream_mode="values"):
        for state in self._states:
            yield state


@pytest.mark.asyncio
async def test_stream_deep_agent_emits_chunks_and_plan():
    states = [
        {
            "messages": [AIMessage(content="Привет")],
            "todos": [{"content": "Шаг 1", "status": "in_progress"}],
        },
        {
            "messages": [AIMessage(content="Привет, мир")],
            "todos": [{"content": "Шаг 1", "status": "completed"}],
        },
    ]
    agent = FakeAgent(states)

    chunks = []
    plans = []

    async def on_chunk(chunk):
        chunks.append(chunk)

    async def on_plan(plan):
        plans.append(plan)

    final_state = await stream_deep_agent(agent, {}, on_chunk=on_chunk, on_plan=on_plan)

    assert final_state["messages"][0].content == "Привет, мир"
    assert chunks == ["Привет", ", мир"]
    assert plans[-1] == todos_to_plan(states[-1]["todos"])
