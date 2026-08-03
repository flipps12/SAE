function borrarFila(elemento) {
    // Busca el checkbox que está dentro del mismo contenedor padre (horario-row o tr)
    const contenedor = elemento.closest('.horario-row') || elemento.closest('tr');
    const checkbox = contenedor.querySelector('input[name$="-DELETE"]');
    
    if (checkbox) { 
        checkbox.checked = true; 
        // Si borramos un horario, ocultamos la fila del horario
        if (contenedor.classList.contains('horario-row')) {
            contenedor.style.display = 'none';
        } else {
            // Si borramos toda la fila de la materia, ocultamos el tr
            contenedor.style.display = 'none';
        }
    }
}