
from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from prompts import WRITE_TODOS_DESCRIPTION
from state import AgentState, TODO



@tool(description=WRITE_TODOS_DESCRIPTION)
def write_todo(
    todos: list[dict],
    tool_id: Annotated[str, InjectedToolCallId]
) -> Command:
    return Command(
        update={
            'todos': todos,
            'messages': [ToolMessage(
                content=f"Updated todo list to {todos}",
                tool_call_id=tool_id
            )]
        }
    )
@tool
def read_todo(state:Annotated[AgentState,InjectedState]):
    """Read the current TODO list from the agent state.

        This tool allows the agent to retrieve and review the current TODO list
        to stay focused on remaining tasks and track progress through complex workflows.

        Args:
            state: Injected agent state containing the current TODO list
        Returns:
            Formatted string representation of the current TODO list
        """
    result = ""
    todo = state.get('todos',[])
    if not todo:
        return f'there is no todo'
    for i,todos in enumerate(todo,1):
        result += f'{i}.{todos.get('status')} - the  content {todos.get('content')}'
    return result

