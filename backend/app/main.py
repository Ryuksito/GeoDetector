from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import video, control, health
from app.services.camera import Camera
from app.services.uart import UART

# Crear la instancia de FastAPI
app = FastAPI()

# Crear una instancia de la cámara
cam = Camera()
cam.start()
uart = UART(port="/dev/ttyUSB0", baud_rate=115200)
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
