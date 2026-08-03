document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('modalMaterias');
    if (!modalElement) return;

    const modal = new bootstrap.Modal(modalElement);
    const nombreSpan = document.getElementById('modalProfesorNombre');
    const cuerpoTabla = document.getElementById('modalMateriasCuerpo');

    document.querySelectorAll('.btn-ver-materias').forEach(boton => {
        boton.addEventListener('click', function(e) {
            e.preventDefault();
            
            const nombre = this.getAttribute('data-profesor-nombre');
            const dictados = JSON.parse(this.getAttribute('data-dictados') || '[]');

            nombreSpan.textContent = nombre;
            cuerpoTabla.innerHTML = '';

            if (dictados.length === 0) {
                cuerpoTabla.innerHTML = `
                    <tr>
                        <td colspan="12" class="text-center text-muted py-4">
                            El docente no posee dictados registrados en el ciclo lectivo activo.
                        </td>
                    </tr>`;
            } else {
                dictados.forEach(d => {
                    // --- LÓGICA DE GRUPO ACTUALIZADA ---
                    let htmlGrupo = `<span class="text-white-50">-</span>`;
                    if (d.grupo && d.grupo !== 'Curso Completo / Único') {
                        // Si es Grupo A o Grupo B, le ponemos un lindo badge e iconito
                        htmlGrupo = `<span class="badge bg-warning text-dark fw-bold"><i class="fa-solid fa-people-group me-1"></i>${d.grupo}</span>`;
                    } else if (d.es_taller) {
                        htmlGrupo = `<span class="fw-bold text-white-50">TALLER</span>`;
                    }

                    let htmlHorarios = `<span class="text-white-50 small">Sin asignar</span>`;
                    if (d.horarios && d.horarios.length > 0) {
                        htmlHorarios = `<div class="d-flex flex-column gap-1">`;
                        d.horarios.forEach(h => {
                            htmlHorarios += `
                                <div class="text-nowrap text-white tabla-celda-horario">
                                    <span class="text-white-50">${h.dia}</span> 
                                    <strong>${h.inicio}-${h.fin}</strong>
                                    <span class="text-white-50 ms-1">(${h.aula})</span>
                                </div>`;
                        });
                        htmlHorarios += `</div>`;
                    }

                    const fila = `
                        <tr class="border-bottom border-secondary-subtle text-nowrap text-white">
                            <td class="ps-3 fw-bold text-wrap tabla-celda-materia">${d.materia_nombre}</td>
                            <td><span class="badge bg-secondary text-uppercase">${d.materia_tipo}</span></td>
                            <td class="font-monospace">${d.pid}</td>
                            <td class="font-monospace">${d.cupof}</td>
                            <td>${d.toma_posesion}</td>
                            <td>${d.forma_ingreso}</td>
                            <td class="fw-semibold">${d.revista}</td>
                            <td class="font-monospace">${d.secuencia}</td>
                            <td><span class="badge bg-primary px-2.5">${d.curso_nombre}</span></td>
                            <td class="text-wrap tabla-celda-especialidad"><small>${d.curso_esp}</small></td>
                            <td>${htmlGrupo}</td>
                            <td class="pe-3">${htmlHorarios}</td>
                        </tr>`;
                    cuerpoTabla.insertAdjacentHTML('beforeend', fila);
                });
            }
            modal.show();
        });
    });
});