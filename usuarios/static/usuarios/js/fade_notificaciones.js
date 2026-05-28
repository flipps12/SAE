document.addEventListener("DOMContentLoaded", function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Animación de desvanecimiento por CSS puro
            alert.style.transition = "opacity 0.5s ease";
            alert.style.opacity = "0";
            
            // Elimina el elemento del HTML cuando termina el fade
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 3000); // 3 segundos visible
    });
});