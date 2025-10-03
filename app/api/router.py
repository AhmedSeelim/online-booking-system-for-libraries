from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/ping")
def ping():
    """Health check endpoint"""
    return {"status": "ok"}