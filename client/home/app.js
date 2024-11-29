document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("video-stream");
    const btnVideo = document.getElementById("btn-video");
    const btnMask = document.getElementById("btn-mask");
    const resetBtn = document.getElementById("reset-hsv");
    const setBtn = document.getElementById("set-hsv")
    const metadataContainer = document.getElementById("metadata-content");

    // Botones de formas
    const btnSquare = document.getElementById("btn-square");
    const btnTriangle = document.getElementById("btn-triangle");
    const btnCircle = document.getElementById("btn-circle");

    async function fetchMetadata() {
        try {
            const response = await fetch("/detection/metadata");
            if (response.ok) {
                const metadata = await response.json();

                // Renderizar los datos en el contenedor
                metadataContainer.innerHTML = Object.entries(metadata)
                    .map(([key, value]) => {
                        const formattedValue = typeof value === 'number' ? value.toFixed(2) : value;
                        return `<p><strong>${key}:</strong> ${formattedValue}</p>`;
                    })
                    .join("");
            } else {
                console.error("Error al obtener los datos del metadata.");
            }
        } catch (error) {
            console.error("Error en la solicitud de metadata: ", error);
        }
    }

    setInterval(fetchMetadata, 1000);

    function updateShape(shape) {
        fetch(`/control/update-shape?shape=${shape}`, {
            method: "PUT",
            headers: {
                "Accept": "application/json",
            },
        })
            .then((response) => {
                if (response.ok) {
                    console.log(`Forma seleccionada: ${shape}`);
                } else {
                    console.error("Error al actualizar la forma seleccionada.");
                }
            })
            .catch((error) => {
                console.error("Error en la solicitud: ", error);
            });
    }

    btnSquare.addEventListener("click", () => updateShape("quadrilateral"));
    btnTriangle.addEventListener("click", () => updateShape("triangle"));
    btnCircle.addEventListener("click", () => updateShape("circle"));

    // Cambiar entre Video y Mask
    btnVideo.addEventListener("click", () => {
        video.src = "/detection/video"; // Cambia la fuente al video normal
    });

    btnMask.addEventListener("click", () => {
        video.src = "/detection/mask"; // Cambia la fuente a la máscara
    });

    // Obtener los valores HSV iniciales desde el servidor
    async function fetchHSV() {
        const response = await fetch("/control/hsv");
        if (response.ok) {
            const hsv = await response.json();

            // Actualizar sliders y sus valores
            document.getElementById("lower-h").value = hsv.lower_h;
            document.getElementById("lower-s").value = hsv.lower_s;
            document.getElementById("lower-v").value = hsv.lower_v;
            document.getElementById("upper-h").value = hsv.upper_h;
            document.getElementById("upper-s").value = hsv.upper_s;
            document.getElementById("upper-v").value = hsv.upper_v;

            document.getElementById("lower-h-value").textContent = hsv.lower_h;
            document.getElementById("lower-s-value").textContent = hsv.lower_s;
            document.getElementById("lower-v-value").textContent = hsv.lower_v;
            document.getElementById("upper-h-value").textContent = hsv.upper_h;
            document.getElementById("upper-s-value").textContent = hsv.upper_s;
            document.getElementById("upper-v-value").textContent = hsv.upper_v;
        } else {
            console.error("Error al obtener los valores HSV del servidor.");
        }
    }

    fetchHSV(); // Llamar a la función para cargar los valores iniciales

    // Sliders para ajustar HSV
    const sliders = ["lower-h", "lower-s", "lower-v", "upper-h", "upper-s", "upper-v"];
    sliders.forEach((id) => {
        const slider = document.getElementById(id);
        const valueDisplay = document.getElementById(`${id}-value`);

        slider.addEventListener("input", () => {
            valueDisplay.textContent = slider.value;

            // Agrupar valores HSV en un objeto
            const hsv = {
                lower_h: parseInt(document.getElementById("lower-h").value),
                lower_s: parseInt(document.getElementById("lower-s").value),
                lower_v: parseInt(document.getElementById("lower-v").value),
                upper_h: parseInt(document.getElementById("upper-h").value),
                upper_s: parseInt(document.getElementById("upper-s").value),
                upper_v: parseInt(document.getElementById("upper-v").value),
            };

            // Enviar los valores HSV al servidor
            fetch(`/control/update-hsv`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(hsv),
            })
                .then((response) => {
                    if (!response.ok) {
                        console.error("Error al actualizar los valores HSV en el servidor.");
                    }
                })
                .catch((error) => {
                    console.error("Error en la solicitud: ", error);
                });
        });
    });

    // Manejar el botón de reset
    resetBtn.addEventListener("click", () => {
        fetch("/control/reset-hsv", {
            method: "POST",
        })
            .then((response) => {
                if (response.ok) {
                    console.log("HSV restablecido correctamente.");
                    fetchHSV(); // Recargar los valores por defecto
                } else {
                    console.error("Error al restablecer los valores HSV.");
                }
            })
            .catch((error) => {
                console.error("Error en la solicitud de restablecimiento:", error);
            });
    });

    setBtn.addEventListener("click", () => {
        const hsv = {
            lower_h: parseInt(document.getElementById("lower-h").value),
            lower_s: parseInt(document.getElementById("lower-s").value),
            lower_v: parseInt(document.getElementById("lower-v").value),
            upper_h: parseInt(document.getElementById("upper-h").value),
            upper_s: parseInt(document.getElementById("upper-s").value),
            upper_v: parseInt(document.getElementById("upper-v").value),
        };

        // Enviar los valores HSV al servidor
        fetch(`/control/update-hsv`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(hsv),
        })
            .then((response) => {
                if (!response.ok) {
                    console.error("Error al actualizar los valores HSV en el servidor.");
                }
            })
            .catch((error) => {
                console.error("Error en la solicitud: ", error);
            });
    });
});
