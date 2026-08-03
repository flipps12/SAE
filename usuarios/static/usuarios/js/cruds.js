document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById('modalEliminar');
    const inputPk = document.getElementById('pkEliminar');

    modal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const id = button.getAttribute('data-id');
        inputPk.value = id;
    });

});
