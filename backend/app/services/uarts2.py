import serial
import json
import threading
import time
import random
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

    def __init__(self, port, baud_rate=115200):
        if not hasattr(self, "_initialized"):
            self.serial_port = serial.Serial(port, baudrate=baud_rate, timeout=1)
            self.running = False
            self.thread = None
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
        if self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    print(f"Recibido del ESP32: <{data}>")
                    if data == "RECEIVING DATA":
                        print("ESP32 listo para recibir datos.")
                        self.receiving_data_ready = True
                    
                    return data
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error al recibir datos: {e}")
                return None

    def _transmit_loop(self):
        try:
            
            while self.running:
                if not self.receiving_data_ready: 
                    self.receive_data()
                else:
                    x = random.random()
                    y = random.random()
                    z = random.random()
                    d = random.random()
                    area = random.random()
                    mensaje = f"{x},{y},{z},{d},{area}\n"
                    self.serial_port.write(mensaje.encode('utf-8'))
                    print(f"Enviado al ESP32: <{mensaje.strip()}>")
                    # self.send_data(cam.metadata)

                    # Esperar una respuesta del ESP32 antes de enviar otro mensaje
                    while True:
                        data = self.receive_data()
                        if data is not None:
                            break

        except serial.SerialException as e:
            print(f"Error de comunicación: {e}")
        except KeyboardInterrupt:
            print("\nFinalizando...")
        finally:
            if self.serial_port.is_open:
                self.serial_port.close()
                print("Puerto serial cerrado.")

    def start(self, port:str=None, baud_rate:int=115200):
        """
        Inicia el hilo de transmisión de datos.
        """
        if not self.running:
            self.running = True
            if not self.serial_port.is_open:
                raise ValueError("missing 1 required positional argument: 'port'")
            self.thread = threading.Thread(target=self._transmit_loop, daemon=True)
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
