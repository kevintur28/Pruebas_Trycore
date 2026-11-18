/* Interacciones pequeñas del calendario. No utiliza librerías externas. */
(function () {
    "use strict";

    const filtro = document.getElementById("format-filter");
    const botonImprimir = document.getElementById("print-calendar");

    function filtrarPublicaciones() {
        if (!filtro) return;

        const formatoSeleccionado = filtro.value;
        const dias = document.querySelectorAll(".day");

        dias.forEach((dia) => {
            const publicaciones = dia.querySelectorAll(".event");
            const mensajeDiaLibre = dia.querySelector(".empty");
            const mensajeSinResultados = dia.querySelector(".filter-empty");
            let visibles = 0;

            publicaciones.forEach((publicacion) => {
                const coincide = formatoSeleccionado === "todos"
                    || publicacion.dataset.format === formatoSeleccionado;

                publicacion.hidden = !coincide;
                if (coincide) visibles += 1;
            });

            if (mensajeDiaLibre) {
                mensajeDiaLibre.hidden = formatoSeleccionado !== "todos";
            }

            if (mensajeSinResultados) {
                mensajeSinResultados.hidden = formatoSeleccionado === "todos" || visibles > 0;
            }
        });
    }

    if (filtro) {
        filtro.addEventListener("change", filtrarPublicaciones);
    }

    if (botonImprimir) {
        botonImprimir.addEventListener("click", function () {
            window.print();
        });
    }
}());
