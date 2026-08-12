document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".fila-dictado").forEach(function(fila) {

        fila.addEventListener("click", function() {
            window.location.href = this.dataset.url;
        });

    });

});