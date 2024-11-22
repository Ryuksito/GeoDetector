from aiortc import MediaStreamTrack
from av import VideoFrame
import cv2
import asyncio

class VideoStreamTrack(MediaStreamTrack):
    """
    Custom WebRTC video stream track that continuously reads frames from OpenCV.
    """
    kind = "video"

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)  # Ajusta el índice si hay más cámaras
        self.running = True  # Indica si la cámara está activa

    async def recv(self):
        while self.running:
            print("running")
            # Leer el siguiente frame desde la cámara
            ret, frame = self.cap.read()
            if not ret:
                print("No se pudo capturar el frame. Deteniendo...")
                self.running = False
                break

            # Procesar el frame (si es necesario)
            # Por ejemplo, convertir a escala de grises: frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Crear un VideoFrame compatible con WebRTC
            video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
            video_frame.pts = None
            video_frame.time_base = None
            return video_frame

    def stop(self):
        print("Cerrando cámara")
        self.running = False
        self.cap.release()
