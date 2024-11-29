from fastapi import APIRouter
from app.services.camera import Camera
from app.utils.helpers import get_json_settings

router = APIRouter(prefix='/health')
cam = Camera()

@router.get("/check", tags=["health"])
async def health_check():
    
    return get_json_settings()
