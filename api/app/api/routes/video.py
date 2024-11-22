from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2

router = APIRouter()

def gen_frames():
    cap = cv2.VideoCapture(0)  # Ajusta el índice de la cámara si es necesario
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Codificar el frame en formato JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield del frame como parte del stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@router.get("/video")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
