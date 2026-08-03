document.addEventListener("DOMContentLoaded", function () {

    const checkboxActivo = document.getElementById("id_activo");
    const contenedorBaja = document.getElementById("contenedor-baja");

    if (!checkboxActivo || !contenedorBaja) return;

    function evaluarEstado() {
        contenedorBaja.style.display = checkboxActivo.checked ? "none" : "block";
    }

    checkboxActivo.addEventListener("change", evaluarEstado);
    evaluarEstado();
});