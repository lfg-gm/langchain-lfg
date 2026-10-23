"""LangChain tools for LFG Alarm.

- ``LfgAlarmToolkit`` gives an agent LFG Alarm's tools, the same ones Claude
  and ChatGPT use, read from the hosted server so they always match it. Needs a
  personal key (``LFG_API_KEY``), made in the LFG Alarm app under
  Settings > AI apps and keys.
- ``LfgRingPhoneTool`` rings an Anything alarm's private link
  (``LFG_RING_URL``) so an agent can get its person's attention. No key.
"""

from __future__ import annotations

import os
from typing import Any, List, Optional

from langchain_core.tools import BaseTool, BaseToolkit, StructuredTool
from lfg_alarm import LfgAlarm, LfgAlarmError, ring
from pydantic import ConfigDict, Field, PrivateAttr


class LfgAlarmToolkit(BaseToolkit):
    """LFG Alarm's tools as LangChain tools.

    Setup:
        Install ``langchain-lfg`` and set ``LFG_API_KEY`` to a personal key from
        the LFG Alarm app (Settings > AI apps and keys).

    Instantiate:
        .. code-block:: python

            from langchain_lfg import LfgAlarmToolkit

            toolkit = LfgAlarmToolkit(only=["set_time_alarm", "list_my_alarms", "delete_alarm"])
            tools = toolkit.get_tools()
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    api_key: Optional[str] = Field(default=None, description="Personal key; defaults to LFG_API_KEY.")
    only: Optional[List[str]] = Field(default=None, description="Tool names to keep, for example ['set_time_alarm'].")
    client: Optional[Any] = Field(default=None, exclude=True, description="An lfg_alarm.LfgAlarm client to use instead.")

    def get_tools(self) -> List[BaseTool]:
        """Reads the tools from LFG Alarm and returns them as LangChain tools."""
        client = self.client or LfgAlarm(api_key=self.api_key)
        listed = client.tools()
        if self.only is not None:
            listed = [t for t in listed if t["name"] in self.only]
        return [_as_tool(client, t) for t in listed]


def _as_tool(client: Any, spec: dict) -> BaseTool:
    name = spec["name"]

    def run(**kwargs: Any) -> str:
        return client.call(name, **kwargs).text

    return StructuredTool(
        name=name,
        description=spec.get("description") or spec.get("title") or name,
        args_schema=spec.get("input_schema") or {"type": "object", "properties": {}},
        func=run,
    )


class LfgRingPhoneTool(BaseTool):
    """Rings the person's phone now through an LFG Alarm Anything alarm.

    Setup:
        Make an Anything alarm in the LFG Alarm app, copy its private link and
        set ``LFG_RING_URL`` to it (or pass ``url``).

    Instantiate:
        .. code-block:: python

            from langchain_lfg import LfgRingPhoneTool

            tool = LfgRingPhoneTool()

    Invoke:
        .. code-block:: python

            tool.invoke({})
    """

    name: str = "ring_phone"
    description: str = (
        "Rings the person's phone now with their LFG Alarm, so they hear it even away from the screen. "
        "Use it when something they asked to be told about is ready or needs them. "
        "It rings the alarm the person set up; nothing written here is shown."
    )
    url: Optional[str] = Field(default=None, description="The alarm's private link; defaults to LFG_RING_URL.")
    _ring: Any = PrivateAttr(default=None)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._ring = ring

    def _run(self, **_: Any) -> str:
        link = self.url or os.environ.get("LFG_RING_URL")
        if not link:
            raise LfgAlarmError(
                "No ring link. Copy an Anything alarm's link from the LFG Alarm app and pass it as url, or set LFG_RING_URL."
            )
        r = self._ring(link)
        if r.rang:
            n = r.woke_up if r.woke_up is not None else 1
            return f"Rang. It reached {n} {'person' if n == 1 else 'people'}."
        return f"Did not ring: {r.message or 'it rang moments ago'}."
