from fastapi import APIRouter
from .auth import router as auth
from .books import router as books
from .resources import router as resources

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth)
api_router.include_router(books)
api_router.include_router(resources)


@api_router.get("/ping")
def ping():
    """Health check endpoint"""
    return {"status": "ok"}