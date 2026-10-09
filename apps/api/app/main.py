from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import secrets
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.routes import router
from app.api.auth import router as auth_router
from app.config import settings
from app.db.models import Base
from app.db.session import engine

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s')

@asynccontextmanager
async def lifespan(_app:FastAPI):
    if settings.auto_create_db:
        async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id=request.headers.get('x-request-id') or secrets.token_hex(12)
        response: Response=await call_next(request)
        response.headers['X-Request-ID']=request_id
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['X-Frame-Options']='DENY'
        return response

app=FastAPI(title='SafeScroll API',version=settings.app_version,docs_url='/docs' if settings.app_env!='production' else None,redoc_url=None,lifespan=lifespan)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=False,allow_methods=['GET','POST'],allow_headers=['Authorization','Content-Type'])
app.include_router(router)
app.include_router(auth_router,prefix='/api/v1')

@app.get('/', include_in_schema=False)
async def root():
    return {
        'service': 'SafeScroll API',
        'status': 'running',
        'version': settings.app_version,
        'docs': '/docs',
        'health': '/api/v1/health',
        'web_frontend': 'http://127.0.0.1:3000',
        'admin_portal': 'http://127.0.0.1:3001'
    }
if settings.metrics_enabled:
    from prometheus_fastapi_instrumentator import routing
    from starlette.routing import Match

    def _patched_get_route_name(scope, routes, route_name=None):
        for route in routes:
            match, child_scope = route.matches(scope)
            if match == Match.FULL:
                route_path = getattr(route, 'path', None) or getattr(route, 'path_format', '')
                child_scope = {**scope, **child_scope}
                sub_routes = getattr(route, 'routes', None) or getattr(getattr(route, 'original_router', None), 'routes', None)
                if sub_routes:
                    sub_name = _patched_get_route_name(child_scope, sub_routes, route_path)
                    if sub_name:
                        return sub_name
                return route_path
            elif match == Match.PARTIAL and route_name is None:
                return getattr(route, 'path', None) or getattr(route, 'path_format', '')
        return None

    routing._get_route_name = _patched_get_route_name
    Instrumentator().instrument(app).expose(app,endpoint='/metrics',include_in_schema=False)
