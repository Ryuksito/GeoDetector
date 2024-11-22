from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2
from app.services.camera import Camera

router = APIRouter()
cam = Camera()

def gen_frames(is_mask:bool=False):
    cap = cv2.VideoCapture(1)  # Ajusta el índice de la cámara si es necesario
    while True:
        frame = cam.get_frame() if not is_mask else cam.get_mask()

        # Codificar el frame en formato JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield del frame como parte del stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@router.get("/video")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.get("/mask")
async def video_feed():
    return StreamingResponse(gen_frames(True), media_type="multipart/x-mixed-replace; boundary=frame")
