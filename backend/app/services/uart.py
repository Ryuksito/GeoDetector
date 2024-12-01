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
            self.rx_thread = None
            self.tx_thead = None
            self.receiving_data_ready = False  # Indica si se recibió "RECEIVING DATA"
            self._initialized = True

    
    def send_data(self, data):
        """
        Envía datos al puerto UART del formato JSON.
        """
        if self.serial_port.is_open and self.receiving_data_ready:
            serial_data = ';'.join([str(v) for v in data.values()]) + '\n'
            self.serial_port.write(serial_data.encode('utf-8'))
            print(f"Enviado: {serial_data}")

    def receive_data(self):
        print(self.serial_port.is_open)
        if self.serial_port.is_open:
            try:
                data = self.serial_port.readline().decode('utf-8').strip()
                print(data)
                if data:
                    print(f"Recibido: {data}")
                    # Verificar si el mensaje recibido es "RECEIVING DATA"

                    if not self.receiving_data_ready:
                        if data == "RECEIVING DATA":
                            self.receiving_data_ready = True
                            print("ESP32 listo para recibir datos.")
                return data
            except Exception as e:
                print(f"Error al recibir datos: {e}")
                return None

    def _rx_task(self):
        while self.running:
            self.receive_data()
            time.sleep(0.1)

    def _tx_task(self):
        while self.running:
            metadata = cam.metadata
            if metadata:
                self.send_data(metadata)
            time.sleep(0.1)

    def start(self):
        """
        Inicia el hilo de transmisión de datos.
        """
        if not self.running:
            self.running = True

            self.running = True
            if not self.serial_port.is_open:
                raise ValueError("missing 1 required positional argument: 'port'")
            
            print(self.serial_port)

            self.rx_thread = threading.Thread(target=self._rx_task, daemon=True)
            self.rx_thread.start()
            
            self.tx_thread = threading.Thread(target=self._tx_task, daemon=True)
            self.tx_thread.start()
            print("Hilo de transmisión UART iniciado.")

    def stop(self):
        """
        Detiene el hilo de transmisión y cierra el puerto UART.
        """
        if self.running:
            self.running = False
            if self.rx_thread and self.rx_thread.is_alive():
                self.rx_thread.join()
            if self.tx_thread and self.tx_thread.is_alive():
                self.tx_thread.join()
            if self.serial_port.is_open:
                self.serial_port.close()
            print("Hilo de transmisión UART detenido y puerto cerrado.")

