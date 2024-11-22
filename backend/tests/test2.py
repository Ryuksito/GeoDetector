import time
from tests.test import Camera
import cv2 


if __name__ == "__main__":
    # Crear una instancia de la cámara
    cam = Camera()

    # Iniciar la cámara en segundo plano
    cam.start()

    try:
        while True:
            # Obtener el frame procesado
            frame = cam.get_frame()
            if frame is not None:
                cv2.imshow("Camera Feed", frame)

            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.01)  # Simula procesamiento adicional

    except KeyboardInterrupt:
        print("Deteniendo la cámara...")

    finally:
        cam.stop()
        cv2.destroyAllWindows()
