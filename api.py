import asyncio
import json
import os
import uuid
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from main import create_review_agent
from typing import Any


app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers = ['*']
)


jobs:dict[str,dict[str,Any]]={}



class ReviewRequest(BaseModel):
    link:str

class JobStatus(BaseModel):
    status:str
    job_id:str
    result:str|None
    todo:list|None



@app.post("/review", response_model=JobStatus)
async def start_review(req:ReviewRequest):
    job_id = str(uuid.uuid4())
    jobs[job_id]={'status':'pending','result':None,'todo':[],'event':asyncio.Event()}
    asyncio.create_task(_run_agent(job_id,req.link))
    return JobStatus(status='pending',job_id=job_id,result=None,todo=[])

async def _run_agent(id,link):
    jobs[id]['status']='running'
    try:
        loop=asyncio.get_event_loop()
        result = await loop.run_in_executor(None,lambda: agent.invoke({
                "messages": [HumanMessage(content=link)]
            }))

        jobs[id]['status']='done'
        jobs[id]['result']=result['messages'][-1].content
        jobs[id]['todo']=result.get('todo',[])

    except Exception as e:
        jobs[id]['result'] = str(e)
        jobs[id]['status']='error'



@app.get("/review/{job_id}/stream")
async def stream_review(job_id:str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return StreamingResponse(
        _sse_generator(job_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")
async def _sse_generator(job_id:str) -> AsyncIterator[str]:
    while True:
        job = jobs.get(job_id)
        if not job:
            yield f"data: {json.dumps({'error': 'job not found'})}\n\n"
            break

        await job['event'].wait()
        job['event'].clear()


        payload={
            "status": job["status"],
            "todo": job.get("todo", []),
            "result": job.get("result"),
        }


        yield f'data:{json.dumps(payload)}\n\n'

        if job['status'] in ['done','error']:
            break






