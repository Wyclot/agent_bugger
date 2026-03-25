import os
from typing import Annotated
from typing_extensions import TypedDict
import json
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
import subprocess

from state import Agent
from prompts import AGENT_PROMPT, REVIEWER_PROMPT, FIXER_PROMPT
from file_tools import ls, read_file, write_file, save_repo
from todo_kit import write_todo, read_todo
from sub_agentss import _create_task_tool, SubAgent

load_dotenv()
def create_review_agent():
    model = init_chat_model(model="openai:gpt-4o-mini")

    reviewer_agent = {
    "name": "reviewer-agent",
    "description": "Reviews a single file and finds bugs",
    "prompt": REVIEWER_PROMPT,
    "tools": ["ls", "read_file"]
    }

    fixer_agent = {
    "name": "fixer-agent",
    "description": "Fixes bugs in a file based on review",
    "prompt": FIXER_PROMPT,
    "tools": ["read_file", "write_file"]
    }


    sub_agent_tools = [ls, read_file, write_file]


    task_tool = _create_task_tool(
        sub_agent_tools,
    [reviewer_agent, fixer_agent],
    model,
    Agent
    )


    all_tools = [save_repo, ls, read_file, write_file, write_todo, read_todo, task_tool]


    agent = create_agent(
    model=model,
    tools=all_tools,
    system_prompt=AGENT_PROMPT,
    state_schema=Agent
    )
    return agent

if __name__ == "__main__":
    agent = create_review_agent()
    url = input("Enter GitHub URL: ")
    response = agent.invoke({
        "messages": [HumanMessage(content=url)]
    })
    print(response["messages"][-1].content)
