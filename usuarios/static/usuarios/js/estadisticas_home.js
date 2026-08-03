document.addEventListener("DOMContentLoaded", function() {
        const dataDiv = document.getElementById('datos-dashboard');
        
        // Función general de renderizado
        // He añadido un parámetro opcional 'label' para evitar el "undefined"
        const render = (id, tipo, labels, data, colors, options = {}, label = '') => {
            const ctx = document.getElementById(id);
            if (ctx) {
                new Chart(ctx, {
                    type: tipo,
                    data: { 
                        labels: labels, 
                        datasets: [{ 
                            label: label, 
                            data: data, 
                            backgroundColor: colors, 
                            borderColor: colors, 
                            fill: tipo === 'line' ? false : true, 
                            tension: 0.4 
                        }] 
                    },
                    options: { 
                        responsive: true, 
                        maintainAspectRatio: false, 
                        ...options 
                    }
                });
            }
        };

        // 1. Trayectorias (Doughnut)
        render('chartTrayectorias', 'doughnut', ['TEA', 'TEP', 'TED'], JSON.parse(dataDiv.dataset.trayectorias), ['#0d6efd', '#198754', '#dc3545']);
        
        // 2. Ausentismo (Bar)
        render('chartAusentismo', 'bar', ['1°', '2°', '3°', '4°', '5°', '6°', '7°'], JSON.parse(dataDiv.dataset.ausentismo), '#0d6efd');
        
        // 3. Notas (Línea sin leyenda)
        render('chartNotas', 'line', ['1C', '2C', 'Final'], JSON.parse(dataDiv.dataset.notas), '#6f42c1', {
            scales: {
                y: { beginAtZero: true, max: 10, ticks: { stepSize: 1 } }
            },
            plugins: {
                legend: { display: false }
            }
        });
        
        // 4. Especialidades (Pie) - Ajustada para leer correctamente los nombres
        // En tu script JS, ahora solo necesitas esto:
        const espNombres = JSON.parse(dataDiv.dataset.espNombres);
        const espValores = JSON.parse(dataDiv.dataset.espValores);

        render('chartEspecialidades', 'pie', espNombres, espValores, ['#0dcaf0', '#fd7e14', '#20c997']);
    });