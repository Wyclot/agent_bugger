from typing_extensions import TypedDict
from typing import Annotated, Literal, NotRequired
from langchain.agents import AgentState
class TODO(TypedDict):
    content:str
    status:Literal['pending','in_process','completed']


def todos_reducer(left,right):
    if right is None:
        return left
    return right
class Agent(AgentState):
    todos:Annotated[NotRequired[list[TODO]], todos_reducer]



