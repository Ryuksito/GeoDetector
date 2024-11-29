import time
import cv2
import cv2
import numpy as np
from typing import Dict, List, Union
from threading import Thread, Lock

REAL_WIDTH = 14.0  # Ancho real del círculo en cm
REAL_DISTANCE = 31.0  # Distancia real en cm

class Camera:
    _instance = None  # Variable de clase para el patrón Singleton
    _lock = Lock()  # Lock para evitar problemas de concurrencia

    def __new__(cls, *args, **kwargs):
        """Singleton: Asegura que solo haya una instancia de la clase."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, camera_index=0):
        if not hasattr(self, "_initialized"):
            # Inicializa la cámara y las variables
            self.camera_index = camera_index
            self.cap = cv2.VideoCapture(camera_index)
            self.frame = None
            self.mask = None
            self.metadata = None
            self.running = False

            # Valores HSV predeterminados
            self.lower_hsv = np.array([40, 40, 90])
            self.upper_hsv = np.array([110, 255, 255])

            # Kernel para operaciones morfológicas
            self.kernel = np.ones((5, 5), np.uint8)

            # Para asegurarnos de no re-inicializar
            self._initialized = True

            self.focal_lenght = 600 # cm, ecuation (width * REAL_DISTANCE) / REAL_WIDTH
            self.cuadrilateral_area = 196 # cm
            self.triangle_area = 119 # cm
            self.circle_area = 154 # cm

    def start(self):
        """Inicia el hilo para capturar frames de la cámara."""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Detiene la captura de la cámara."""
        self.running = False
        self.cap.release()

    def get_frame(self):
        """Obtiene el último frame capturado."""
        return self.frame

    def get_mask(self):
        """Obtiene el último frame capturado."""
        return self.mask

    def set_hsv(self, lower: Union[List[int], None], upper: Union[List[int], None]):
        """Configura los rangos HSV."""
        if lower is not None and len(lower) == 3:
            self.lower_hsv = np.array(lower)
        if upper is not None and len(upper) == 3:
            self.upper_hsv = np.array(upper)

    def custom_set_hsv(self, values:Dict[str, int]):
        """
        Configura los rangos HSV de la cámara.


        Parámetros:
            values (Dict[str, int]):
                Un diccionario que puede contener las siguientes claves:
                - 'lh': (int) Valor del límite inferior del tono (Hue).
                - 'ls': (int) Valor del límite inferior de la saturación (Saturation).
                - 'lv': (int) Valor del límite inferior del brillo (Value).
                - 'uh': (int) Valor del límite superior del tono (Hue).
                - 'us': (int) Valor del límite superior de la saturación (Saturation).
                - 'uv': (int) Valor del límite superior del brillo (Value).

                Cualquier clave no incluida o con valor `None` no se actualizará.
        """
        if values.get('lh') is not None:
            self.lower_hsv[0] = values.get('lh')
        if values.get('ls') is not None:
            self.lower_hsv[1] = values.get('ls')
        if values.get('lv') is not None:
            self.lower_hsv[2] = values.get('lv')
        if values.get('uh') is not None:
            self.upper_hsv[0] = values.get('uh')
        if values.get('us') is not None:
            self.upper_hsv[1] = values.get('us')
        if values.get('uv') is not None:
            self.upper_hsv[2] = values.get('uv')

    def _loop(self):
        """Captura y procesa frames en segundo plano."""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Convertir a HSV y aplicar la máscara
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
            mask = cv2.erode(mask, self.kernel)
            
            # declaracion de variables de medicion
            distance = .0
            area = .0
            x_dobj = .0
            y_dobj = .0
            z_dobj = .0

            # Obtener contornos
            contours = self._get_contours(mask)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                
                if area > 400:
                    approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
                    if len(approx) >= 3 and len(contours) <= 20:
                        distance = self._shape_detection(approx, area, frame)
                        x_dobj, y_dobj, z_dobj = self._calculate_xy_distance(frame.shape, distance, cnt, frame)

            # Actualizar el frame y los metadatos
            self.frame = frame
            self.mask = mask
            self.metadata = {
                'frame_width': frame.shape[1],
                'frame_height': frame.shape[0],
                'x_dobj': x_dobj,
                'y_dobj': y_dobj,
                'z_dobj': z_dobj,
                'dobj': distance,
                'area': area,
            }

    def _shape_detection(self, approx, area, frame):
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        distance = 0

        cv2.drawContours(frame, [approx], 0, (0, 255, 0), 5)
        if len(approx) == 3:
            distance = np.sqrt((self.triangle_area * self.focal_lenght**2) / area)
            cv2.putText(frame, f"T:{distance}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        elif len(approx) == 4:
            distance = np.sqrt((self.cuadrilateral_area * self.focal_lenght**2) / area)
            cv2.putText(frame, f"Cu:{distance} cm", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        elif 7 < len(approx) < 20:
            distance = np.sqrt((self.circle_area * self.focal_lenght**2) / area)
            cv2.putText(frame, f"Ci:{distance}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return distance
        
    def _calculate_xy_distance(self, img_size, distance, cnt, frame):
        """
        Esta funcion a partir de la distancia debe descomoner esa distancia en coordenadas x y
        """
        width = img_size[1]
        heigth = img_size[0]

        x_dobj = 0.
        y_dobj = 0.
        z_dobj = distance

        M = cv2.moments(cnt)
        if M["m00"] != 0:  # Evita división por cero
            x_obj = int(M["m10"] / M["m00"])
            y_obj = int(M["m01"] / M["m00"])
        else:
            x_obj, y_obj = 0, 0

        x_relative = x_obj - width / 2
        y_relative = heigth / 2 - y_obj  # Invertir eje Y


        factor = (z_dobj / self.focal_lenght)
        x_dobj = x_relative * factor
        y_dobj = y_relative * factor


        cv2.circle(frame, (int(x_obj), int(y_obj)), 5, (0, 0, 255), -1)
        cv2.circle(frame, (width // 2, heigth // 2), 5, (0, 255, 0), -1)
        print(f'x: {x_dobj}, y: {y_dobj}, z: {z_dobj}')

        return (x_dobj, y_dobj, z_dobj)

    def _get_contours(self, mask):
        """Obtiene los contornos de la máscara."""
        if int(cv2.__version__[0]) > 3:
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours

if __name__ == "__main__":
    # Crear una instancia de la cámara
    cam = Camera(0)
    print('Config: ', id(cam))

    # Iniciar la cámara en segundo plano
    cam.start()

    def lh(value):
        cam.custom_set_hsv({'lh': value})
    def ls(value):
        cam.custom_set_hsv({'ls': value})
    def lv(value):
        cam.custom_set_hsv({'lv': value})
    def uh(value):
        cam.custom_set_hsv({'uh': value})
    def us(value):
        cam.custom_set_hsv({'us': value})
    def uv(value):
        cam.custom_set_hsv({'uv': value})
    def fl(value):
        cam.focal_lenght = value

    cv2.namedWindow("Trackbars")
    cv2.createTrackbar("L-H", "Trackbars", 0, 180, lh)
    cv2.createTrackbar("L-S", "Trackbars", 0, 255, ls)
    cv2.createTrackbar("L-V", "Trackbars", 0, 255, lv)
    cv2.createTrackbar("U-H", "Trackbars", 0, 180, uh)
    cv2.createTrackbar("U-S", "Trackbars", 0, 255, us)
    cv2.createTrackbar("U-V", "Trackbars", 0, 255, uv)
    cv2.createTrackbar("FL", "Trackbars", cam.focal_lenght, 1000, fl)

    try:
        while True:
            frame = cam.get_frame()
            mask = cam.get_mask()

            # print('HSV: ', cam.lower_hsv, cam.upper_hsv)

            cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
            if frame is not None:
                cv2.resizeWindow("Video", frame.shape[1], frame.shape[0])
                cv2.imshow("Camera Config", frame)
            if mask is not None:
                cv2.imshow("Mask", mask)

            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Deteniendo la cámara...")

    finally:
        cam.stop()
        cv2.destroyAllWindows()
