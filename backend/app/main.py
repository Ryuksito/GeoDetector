import asyncio
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import video, control, health
from app.services.camera import Camera
from app.services.uart import UART

from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    cam = Camera()
    cam.start()

    port = os.getenv("LINUX-UART-PORT") if os.name == "posix" else os.getenv("WINDOWS-UART-PORT")
    uart = UART(port=port, baud_rate=115200)
    uart.start()
    print("Servicios inicializados.")

    try:
        yield
    except asyncio.CancelledError:
        print("Cancelación detectada, asegurando limpieza...")
    finally:
        print("Cerrando aplicación...")

        # Detener los servicios
        try:
            uart.stop()
            cam.stop()
            print("Servicios detenidos.")
        except Exception as e:
            print(f"Error al detener servicios: {e}")


# Crear la instancia de FastAPI
app = FastAPI(lifespan=lifespan)


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
