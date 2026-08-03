document.addEventListener('DOMContentLoaded', function() {
        // Seleccionamos todos los botones de borrar
        document.querySelectorAll('.btn-outline-danger').forEach(button => {
            button.addEventListener('click', function() {
                // Buscamos la fila (tr) más cercana
                const row = this.closest('tr');
                
                // Aplicamos efecto visual antes de ocultar
                row.style.transition = "opacity 0.3s ease";
                row.style.opacity = "0";
                
                // Ocultamos la fila tras terminar la animación
                setTimeout(() => {
                    row.style.display = 'none';
                }, 300);
            });
        });
    });