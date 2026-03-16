from typing_extensions import TypedDict
from typing import Annotated, Literal, NotRequired
from langchain.agents import AgentState
class TODO(TypedDict):
    content:str
    status:Literal['pending','in_process','completed']



class Agent(AgentState):
    todos:NotRequired[list[TODO]]



