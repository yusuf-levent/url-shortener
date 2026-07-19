from fastapi import FastAPI,Request,HTTPException,status
from fastapi.responses import JSONResponse
from routers import links,users,redirect,analytics,admin
from utils import get_ip_hash
from loguru import logger
import services.logging_service
status.ht


app=FastAPI(
    title="Url Shortener API",
    version="1.0.0",
    description="Url shortening, QR, redirect tracking and analytics API "
)
@app.middleware("http")
async def ip_logger_middleware(request:Request,call_next):
    ip_hash=get_ip_hash(request)
    request.state.ip_hash=ip_hash
    with logger.contextualize(ip=ip_hash):
        response=await call_next(request)
        return response
    
@app.exception_handler(HTTPException)
async def custom_http_excetion_handler(request:Request,exc:HTTPException):
    log_message=f"HTTP Error {exc.status_code} | Detail: {exc.detail} | Path: {request.url.path}"
    if exc.status_code==401:
        logger.bind(category="auth").warning(log_message)
    elif exc.status_code in [403,429]:
        logger.bind(category="security").warning(log_message)
    elif exc.status_code in [400,422]:
        logger.warning(log_message)
    else:
        logger.error(log_message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail":exc.detail}
    )



@app.get("/health",tags=["system"])
def health():
    return {"status":"ok","version":"1.0.0"}

app.include_router(links.router)
app.include_router(users.router)
app.include_router(redirect.router)
app.include_router(analytics.router)
app.include_router(admin.router)
