// Generar partículas animadas
const particlesContainer = document.getElementById('particles');
for (let i = 0; i < 50; i++) {
    const particle = document.createElement('div');
    particle.classList.add('particle');
    const size = Math.random() * 5 + 2;
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 6 + 's';
    particle.style.animationDuration = Math.random() * 4 + 4 + 's';
    particlesContainer.appendChild(particle);
}

// Efecto de carga al enviar
const form = document.getElementById('loginForm');
const btn = document.getElementById('loginBtn');

if (form) {
    form.addEventListener('submit', function() {
        btn.classList.add('loading');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ingresando...';
    });
}

// Si hay error, agregar animación de error
const card = document.querySelector('.login-card');
if (card && window.location.search.includes('error')) {
    card.classList.add('error-shake');
    setTimeout(() => {
        card.classList.remove('error-shake');
    }, 400);
}