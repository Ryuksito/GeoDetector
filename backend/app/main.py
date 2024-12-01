from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import video, control, health
from app.services.camera import Camera
from app.services.uart import UART
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

# Crear la instancia de FastAPI
app = FastAPI()

# Crear una instancia de la cámara
cam = Camera()
cam.start()

port = os.getenv("LINUX-UART-PORT") if os.name == "posix" else os.getenv("WINDOWS-UART-PORT")
uart = UART(port=port, baud_rate=115200)
uart.start()

# Incluir las rutas de video
app.include_router(video.router)
app.include_router(control.router)
app.include_router(health.router)

# Montar la carpeta estática para servir los archivos HTML, CSS y JS
app.mount("/static", StaticFiles(directory="../client/home"), name="static")

@app.get("/")
async def root():
    """
    Redirige a la página principal de la aplicación.
    """
    return FileResponse("../client/home/index.html")
