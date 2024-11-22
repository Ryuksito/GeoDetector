from fastapi import FastAPI
from app.api.routes import video
from app.services.camera import Camera

app = FastAPI()
cam = Camera(camera_index=0)
cam.start()

# Incluir las rutas de video
app.include_router(video.router)

@app.get("/")
async def root():
    return {"message": "API funcionando correctamente"}
