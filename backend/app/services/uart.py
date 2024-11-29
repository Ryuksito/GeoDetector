import serial
import json
import threading
import time
from app.services.camera import Camera

cam = Camera()

class UART:
    _instance = None  # Variable de clase para el patrón Singleton
    _lock = threading.Lock()  # Lock para evitar problemas de concurrencia

    def __new__(cls, *args, **kwargs):
        """Singleton: Asegura que solo haya una instancia de la clase."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, port="/dev/ttyUSB0", baud_rate=115200):
        if not hasattr(self, "_initialized"):
            self.serial_port = serial.Serial(port, baudrate=baud_rate, timeout=1)
            self.running = False
            self.thread = None
            self._initialized = True

    def send_data(self, data):
        """
        Envía datos al puerto UART en formato JSON.
        """
        if self.serial_port.is_open:
            serial_data = ';'.join([str(v) for v in data.values()])
            self.serial_port.write(serial_data.encode('utf-8'))
            print(f"Enviado: {serial_data}")

    def receive_data(self):
        """
        Recibe datos desde el puerto UART y los imprime.
        """
        if self.serial_port.is_open:
            try:
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:
                    print(f"Recibido: {data}")
            except Exception as e:
                print(f"Error al recibir datos: {e}")

    def _transmit_loop(self):
        """
        Bucle interno que envía y recibe datos continuamente mientras `self.running` es True.
        """
        while self.running:
            try:
                # Enviar los datos de `cam.metadata`
                metadata = cam.metadata
                if metadata:
                    self.send_data(metadata)

                # Recibir datos desde el ESP32
                self.receive_data()
            except Exception as e:
                print(f"Error en la transmisión/recepción: {e}")
            finally:
                time.sleep(0.5)  # Intervalo entre transmisiones y recepciones

    def start(self):
        """
        Inicia el hilo de transmisión de datos.
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._transmit_loop)
            self.thread.start()
            print("Hilo de transmisión UART iniciado.")

    def stop(self):
        """
        Detiene el hilo de transmisión y cierra el puerto UART.
        """
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            self.serial_port.close()
            print("Hilo de transmisión UART detenido y puerto cerrado.")
