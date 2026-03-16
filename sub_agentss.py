from typing import Annotated, NotRequired
from typing_extensions import TypedDict
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState  # updated 1.0
from langchain.agents import create_agent  # updated 1.0
from langgraph.types import Command
from prompts import TASK_DESCRIPTION_PREFIX
from state import Agent




class SubAgent(TypedDict):
    name:str
    description:str
    prompt:str
    tools:NotRequired[list[str]]
def _create_task_tool(tools,subagents:list[SubAgent],model,state_schema):
    agents = {}
    tools_name={}
    for t in tools:
        if not isinstance(t,BaseTool):
            t=tool(t)
        tools_name[t.name]=t

    for t in subagents:
        if 'tools' in t:
            _tools = [tools_name[t] for t in t['tools']]
        else:
            _tools = tools
        agents[t['name']]=create_agent(model=model,system_prompt=agents['prompt'],tools=_tools,state_schema=state_schema)

    other_agents = [f' {_agenti['name']} : {_agenti['description']} ' for _agenti in subagents ]

    @tool(description = TASK_DESCRIPTION_PREFIX.format(other_agents=other_agents))
    def task(description:str,subagent_type:str,state:Annotated[Agent,InjectedState],id_call=Annotated[str,InjectedToolCallId]):
        state['messages']=[{'role':'user','content':description}]
        if subagent_type not in agents:
            return 'there is no such subagent type'
        sub_agent=agents[subagent_type]
        result = sub_agent.invoke(state)
        return Command(
            update = {
                'messages':[ToolMessage(result['messages'][-1].content, tool_call_id=id_call)]
            }
        )

    return task