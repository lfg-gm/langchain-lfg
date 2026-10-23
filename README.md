# langchain-lfg

LangChain tools for [LFG Alarm](https://lfg.gm): let an agent set real alarms that ring on a person's phone, and their friends' phones, at a time or when something happens online. Or give it one tool that rings the person's phone when a long task is done.

LFG Alarm is a social alarm clock for iPhone and Android. Rocco, LFG's agent, rings a real alarm, not a quiet notification.

```bash
pip install -U langchain-lfg
```

## LfgAlarmToolkit

LFG Alarm's tools, the same ones Claude and ChatGPT use through its MCP server, read from the hosted server so they always match it. Make a personal key in the LFG Alarm app (**Settings** > **AI apps and keys**) and set `LFG_API_KEY`.

```python
from langchain.agents import create_agent
from langchain_lfg import LfgAlarmToolkit

tools = LfgAlarmToolkit(only=["set_time_alarm", "list_my_alarms", "delete_alarm"]).get_tools()
agent = create_agent("openai:gpt-5-mini", tools)
agent.invoke({"messages": [{"role": "user", "content": "Wake me at 7 on weekdays with something upbeat. I'm in London."}]})
```

Leave out `only` to give the agent every tool (price, post, event, trader and webhook alarms, sharing, wallpapers and more).

## LfgRingPhoneTool

Rings the person's phone now through an 🔮 Anything alarm, so they hear it away from the screen. No key: make an Anything alarm in the app, copy its private link and set `LFG_RING_URL`. Anything alarms need a paid plan; see [lfg.gm](https://lfg.gm).

```python
from langchain_lfg import LfgRingPhoneTool

tools = [LfgRingPhoneTool(), *your_tools]
```

The phone shows the alarm's own name, not the agent's words, so name the alarm for the moment, like "Your report is ready". On Android it rings full screen; on iPhone it arrives as a time-sensitive alert with the alarm's sound.

## Develop

```bash
pip install -e ".[test]"
pytest tests
```

Some alarm types and limits depend on the account's plan. For plans and pricing, go to [lfg.gm](https://lfg.gm). Built on the [lfg-alarm](https://pypi.org/project/lfg-alarm/) client. MIT licence. Help: [lfg.gm/support](https://lfg.gm/support) or support@lfg.gm.
