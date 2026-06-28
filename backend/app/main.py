import sys
import os
# Add the 'backend' directory to sys.path so 'app' can be imported as a module
sys.path.append(os.path.join(os.getcwd(), "backend"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import auth_controller, category_controller, tag_controller, transaction_controller, import_controller, portability_controller, recurring_controller, savings_goal_controller, budget_controller, analytics_controller, notification_controller
from app.middleware.logging_middleware import LoggingMiddleware, setup_logging

setup_logging()
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(title="Daily Expense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

app.include_router(auth_controller.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(category_controller.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(tag_controller.router, prefix="/api/v1/tags", tags=["tags"])
app.include_router(transaction_controller.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(import_controller.router, prefix="/api/v1/import", tags=["import"])
app.include_router(portability_controller.router, prefix="/api/v1/portability", tags=["portability"])
app.include_router(recurring_controller.router, prefix="/api/v1/recurring", tags=["recurring"])
app.include_router(savings_goal_controller.router, prefix="/api/v1/goals", tags=["goals"])
app.include_router(budget_controller.router, prefix="/api/v1/budgets", tags=["budgets"])
# Prometheus Instrumentator for metrics
Instrumentator().instrument(app).expose(app)

app.include_router(analytics_controller.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(notification_controller.router, prefix="/api/v1/notifications", tags=["notifications"])



@app.get("/actuator/health")
def health():
    return {"status": "ok"}
