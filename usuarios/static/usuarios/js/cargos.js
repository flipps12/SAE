// static/js/cargos.js

function borrarFila(elemento) {
    // Busca el checkbox que está en la misma fila (tr) del botón presionado
    const fila = elemento.closest('tr');
    const checkboxBorrar = fila.querySelector('input[type="checkbox"][name$="-DELETE"]');
    
    if (checkboxBorrar) {
        checkboxBorrar.checked = true; // Marca el checkbox de DELETE de Django
        fila.style.display = 'none';   // Oculta la fila visualmente
    }
}