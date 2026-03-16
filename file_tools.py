
from langchain_core.tools import  tool
from prompts import LS_DESCRIPTION

import os
import subprocess

@tool(description=LS_DESCRIPTION)
def ls(file:str='.')-> list[str]:
    if file=='.':
        return os.listdir(f'repos/project/')
    else:
        return os.listdir(f'repos/project/{file}')
@tool(description='Use this to read a file from the cloned repository. Pass the file path relative to the project root, e.g. "main.py" or "utils/helpers.py"')
def read_file(file):
    with open(f'repos/project/{file}','r') as f:
        return f.read()
@tool(description='Use this to save fixed code to a file. Pass the file path and the corrected content.')
def write_file(file,content):
    with open(f'repos/project/{file}', 'w') as f:
        f.write(content)
    return f'saved to {file}'

@tool(description='Use this first to clone a GitHub repository before doing anything else. Pass the full GitHub URL.')
def save_repo(url):
    if not os.path.exists('repo'):
        os.mkdir('repo')
    subprocess.run(['git', 'clone', url, 'repos/project'])
    return "repo cloned successfully"
