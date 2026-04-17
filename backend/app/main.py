from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from .routers import auth, patients, doctors, common, chat, indicators, report_types, hospitals, diseases, reports, medications, education, medications_dict, dashboard, imaging_checks, feedback, usage_guides, members, notifications, files, upload
import time
import json

from .database import engine, Base
from .config import settings
from .logging_config import setup_logging, get_logger

setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    max_bytes=settings.LOG_MAX_BYTES,
    backup_count=settings.LOG_BACKUP_COUNT,
    enable_console=settings.LOG_ENABLE_CONSOLE,
    enable_file=settings.LOG_ENABLE_FILE,
)

logger = get_logger(__name__)
logger.info("Starting HealthMonitor API...")

Base.metadata.create_all(bind=engine)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "client_ip": request.client.host if request.client else None,
        }
        
        if response.status_code >= 400:
            logger.error(f"Request failed: {json.dumps(log_data)}")
        else:
            logger.info(f"Request completed: {json.dumps(log_data)}")
        
        return response

app = FastAPI(
    title="HealthMonitor API",
    description="Backend for Chronic Disease Monitoring App",
    version="1.0.0"
)

app.add_middleware(RequestLoggingMiddleware)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(common.router)
app.include_router(chat.router)
app.include_router(indicators.router)
app.include_router(report_types.router)
app.include_router(imaging_checks.router)
app.include_router(hospitals.router)
app.include_router(diseases.router)
app.include_router(reports.router)
app.include_router(medications.router)
app.include_router(education.router)
app.include_router(medications_dict.router)
app.include_router(dashboard.router)
app.include_router(feedback.router)
app.include_router(usage_guides.router)
app.include_router(members.router)
app.include_router(notifications.router)
app.include_router(files.router)
app.include_router(upload.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to HealthMonitor API"}
