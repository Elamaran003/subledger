from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import get_settings
from app.db import init_db
from app.exceptions import DomainError
from app.routes import customers, invoices, ledger, payments, plans, subscriptions


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=get_settings().app_name,
        description="Simplified SaaS billing backend: plans, subscriptions, invoices, payments, ledger.",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        # Safety net: DB constraints caught a race the service-level checks missed.
        return JSONResponse(status_code=409, content={"detail": "Conflict: a database constraint was violated."})

    for module in (plans, customers, subscriptions, invoices, payments, ledger):
        app.include_router(module.router)

    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
