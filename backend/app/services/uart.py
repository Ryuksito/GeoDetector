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

    def __init__(self, port=None, baud_rate=115200):
        if not hasattr(self, "_initialized"):
            try:
                self.serial_port = serial.Serial(port, baudrate=baud_rate, timeout=1)
            except:
                self.serial_port = None
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
        if self.serial_port.is_open and self.receiving_data_ready and (data['dobj'] > 0):
            serial_data = ';'.join([str(v) for v in data.values()]) + '\n'
            self.serial_port.write(serial_data.encode('utf-8'))
            print(f"Sended: {serial_data}")
            self.receiving_data_ready = False


    def receive_data(self):
        if self.serial_port.is_open:
            try:
                raw_data = self.serial_port.readline()
                data = raw_data.decode('utf-8').strip()
                if data:
                    print(f"Recibido: {data}")
                    # Verificar si el mensaje recibido es "RECEIVING DATA"

                    if not self.receiving_data_ready:
                        if data == "RECEIVING DATA":
                            self.receiving_data_ready = True
                            print("ESP32 listo para recibir datos.")
                return data
            except Exception as e:
                print(f"Error al recibir datos: {e}, data: {raw_data}")
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
        if not self.running and self.serial_port is not None:
            self.running = True

            self.running = True
            
            print(self.serial_port)

            self.rx_thread = threading.Thread(target=self._rx_task, daemon=True)
            self.rx_thread.start()
            
            self.tx_thread = threading.Thread(target=self._tx_task, daemon=True)
            self.tx_thread.start()

            print("Hilo de transmisión UART iniciado.")
        else: 
            print("No se inicializo el uart: ", self.serial_port)

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

