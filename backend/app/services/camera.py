import cv2
import numpy as np
from typing import Dict, List, Union
from threading import Thread, Lock
from app.models.hsv import HSV
from app.models.shapes import ShapeType, Shape, SelectShapes
from app.utils.helpers import get_json_settings, set_json_settings


class Camera:
    _instance = None  # Variable de clase para el patrón Singleton
    _lock = Lock()  # Lock para evitar problemas de concurrencia

    def __new__(cls, *args, **kwargs):
        """Singleton: Asegura que solo haya una instancia de la clase."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            config = get_json_settings()

            # Inicializa la cámara y las variables
            self.camera_index = config['cam_idx']
            self.cap = cv2.VideoCapture(self.camera_index)
            self.frame = None
            self.mask = None
            self.metadata = {
                "x_dobj": 0,
                "y_dobj": 0,
                "z_dobj": 0,
                "dobj": 0,
                "area": 0
            }
            self.running = False

            # Valores HSV predeterminados
            self.hsv = HSV(
                lower_hsv = np.array(config['lower_hsv']),
                upper_hsv = np.array(config['upper_hsv'])
            )

            # Kernel para operaciones morfológicas
            self.kernel = np.ones(config['kernel_shape'], np.uint8)

            # Para asegurarnos de no re-inicializar
            self._initialized = True

            self.focal_lenght = config['focal_lenght'] # cm, ecuation (width * REAL_DISTANCE) / REAL_WIDTH
            if config['target_shape'] == SelectShapes.QUADRILATERAL:
                self.target_shape: Shape = ShapeType.QUADRILATERAL.value
            elif config['target_shape'] == SelectShapes.TRIANGLE:
                self.target_shape: Shape = ShapeType.TRIANGLE.value
            elif config['target_shape'] == SelectShapes.CIRCLE:
                self.target_shape: Shape = ShapeType.CIRCLE.value
            else: self.target_shape = ShapeType.QUADRILATERAL.value

    def start(self):
        """Inicia el hilo para capturar frames de la cámara."""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Detiene la captura de la cámara."""
        self.running = False
        if self.running:
            self.running = False
            if self.thread and self.thread.is_alive():
                self.thread.join()
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
            self.hsv.lower_hsv = np.array(lower)
        if upper is not None and len(upper) == 3:
            self.hsv.upper_hsv = np.array(upper)
    
    def set_shape(self, shape: Shape):
        self.target_shape = shape

    def reset_hsv(self):
        """Restablece los rangos HSV predeterminados."""
        self.set_hsv(np.array([40, 40, 90]), np.array([110, 255, 255]))

    def set_camera(self, camera_index: int):
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index)

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
            self.hsv.lower_hsv[0] = values.get('lh')
        if values.get('ls') is not None:
            self.hsv.lower_hsv[1] = values.get('ls')
        if values.get('lv') is not None:
            self.hsv.lower_hsv[2] = values.get('lv')
        if values.get('uh') is not None:
            self.hsv.upper_hsv[0] = values.get('uh')
        if values.get('us') is not None:
            self.hsv.upper_hsv[1] = values.get('us')
        if values.get('uv') is not None:
            self.hsv.upper_hsv[2] = values.get('uv')

    def _loop(self):
        """Captura y procesa frames en segundo plano."""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Convertir a HSV y aplicar la máscara
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array(self.hsv.lower_hsv), np.array(self.hsv.upper_hsv))
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

        

        if self.target_shape.eval_sides(len(approx)):
            cv2.drawContours(frame, [approx], 0, (0, 255, 0), 5)
            distance = np.sqrt((self.target_shape.AREA * self.focal_lenght**2) / area)
            cv2.putText(frame, f"{self.target_shape}:{distance}", (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

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

        return (x_dobj, y_dobj, z_dobj)

    def _get_contours(self, mask):
        """Obtiene los contornos de la máscara."""
        if int(cv2.__version__[0]) > 3:
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours
    
