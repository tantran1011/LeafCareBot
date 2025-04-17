from fastapi import Request
import time 

async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    print(f"request {request.url} with method {request.method} process in {duration:.2f} second") 
    return response