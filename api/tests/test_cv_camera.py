import cv2

def test_camera():
    # Abrir la cámara (ajusta el índice si tienes múltiples cámaras)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se puede acceder a la cámara.")
        return

    print("Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer el frame.")
            break

        # Mostrar el frame en una ventana
        cv2.imshow("Frame", frame)

        # Salir al presionar 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera()
