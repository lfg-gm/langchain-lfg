from types import SimpleNamespace
from typing import Type

from langchain_tests.unit_tests import ToolsUnitTests

from langchain_lfg import LfgAlarmToolkit, LfgRingPhoneTool


class FakeClient:
    def __init__(self):
        self.calls = []

    def tools(self):
        return [
            {"name": "set_time_alarm", "description": "Sets an alarm.", "input_schema": {
                "type": "object", "properties": {"time": {"type": "string"}, "time_zone": {"type": "string"}}, "required": ["time", "time_zone"]}},
            {"name": "list_my_alarms", "description": "Lists alarms.", "input_schema": {"type": "object", "properties": {}}},
        ]

    def call(self, name, **args):
        self.calls.append((name, args))
        return SimpleNamespace(text=f"{name} done")


def test_toolkit_turns_server_tools_into_langchain_tools():
    client = FakeClient()
    tools = LfgAlarmToolkit(client=client, only=["set_time_alarm"]).get_tools()
    assert [t.name for t in tools] == ["set_time_alarm"]
    assert tools[0].invoke({"time": "07:00", "time_zone": "Europe/London"}) == "set_time_alarm done"
    assert client.calls == [("set_time_alarm", {"time": "07:00", "time_zone": "Europe/London"})]


def test_ring_phone_rings_and_says_so():
    tool = LfgRingPhoneTool(url="https://api.lfg.gm/horn/abc")
    tool._ring = lambda url: SimpleNamespace(rang=True, woke_up=1, message=None)
    assert tool.invoke({}) == "Rang. It reached 1 person."


def test_ring_phone_cooling_down_is_told_not_raised():
    tool = LfgRingPhoneTool(url="https://api.lfg.gm/horn/abc")
    tool._ring = lambda url: SimpleNamespace(rang=False, woke_up=None, message="It can go again in 40s.")
    assert tool.invoke({}).startswith("Did not ring")


class TestLfgRingPhoneToolStandard(ToolsUnitTests):
    @property
    def tool_constructor(self) -> Type[LfgRingPhoneTool]:
        return LfgRingPhoneTool

    @property
    def tool_constructor_params(self) -> dict:
        return {"url": "https://api.lfg.gm/horn/abcdefghijklmnopqrstuvwxyz012345"}

    @property
    def tool_invoke_params_example(self) -> dict:
        return {}
