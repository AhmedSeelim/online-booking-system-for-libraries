from fastapi import APIRouter
from ..api import auth, books, resources, bookings

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(books.router)
api_router.include_router(resources.router)
api_router.include_router(bookings.router)


@api_router.get("/ping")
def ping():
    """Health check endpoint"""
    return {"status": "ok"}