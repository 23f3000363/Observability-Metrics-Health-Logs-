from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import time, uuid
from collections import deque

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

EMAIL = "23f3000363@ds.study.iitm.ac.in"
start = time.time()
counter = 0
logs = deque(maxlen=200)

@app.middleware("http")
async def count_and_log(request: Request, call_next):
    global counter
    counter += 1
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    logs.append({
        "level": "info",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "path": request.url.path,
        "request_id": rid
    })
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response

@app.get("/work")
def work(n: int = 1):
    return {"email": EMAIL, "done": n}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return f"""# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total {counter}
"""

@app.get("/healthz")
def healthz():
    return {"status": "ok", "uptime_s": time.time() - start}

@app.get("/logs/tail")
def tail(limit: int = Query(10, ge=1, le=100)):
    return list(logs)[-limit:]