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
            json_data = json.dumps(data)
            self.serial_port.write((json_data + '\n').encode('utf-8'))
            print(f"Enviado: {json_data}")

    def _transmit_loop(self):
        """
        Bucle interno que envía datos continuamente mientras `self.running` es True.
        """
        while self.running:
            try:
                # Obtiene los datos de `get_metadata`
                metadata = cam.metadata
                if metadata:
                    self.send_data(metadata)
            except Exception as e:
                print(f"Error en la transmisión: {e}")
            finally:
                time.sleep(0.5)  # Intervalo entre transmisiones

    def start(self):
        """
        Inicia el hilo de transmisión de datos.

        Args:
            get_metadata (callable): Función para obtener los datos que se enviarán por UART.
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


# Ejemplo de uso
if __name__ == "__main__":
    from app.services.camera import Camera  # Asegúrate de importar correctamente la clase Camera

    # Instancia de la cámara (Singleton)
    cam = Camera()

    # Instancia de UART (Singleton)
    uart = UART(port="/dev/ttyUSB0", baud_rate=115200)

    try:
        # Inicia el hilo de transmisión UART con los datos de la cámara
        uart.start(lambda: cam.metadata)

        print("Presiona Ctrl+C para detener el programa.")

        # Hilo principal permanece activo para otras tareas
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Deteniendo...")
        uart.stop()
    except Exception as e:
        print(f"Error: {e}")
        uart.stop()
