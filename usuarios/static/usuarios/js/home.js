// Canvas de partículas
const canvas = document.createElement('canvas');
canvas.id = 'particles-canvas';
document.body.appendChild(canvas);

const ctx = canvas.getContext('2d');
let particles = [];
let particleCount = 100;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

function createParticles() {
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 3 + 1,
            speedX: (Math.random() - 0.5) * 0.5,
            speedY: (Math.random() - 0.5) * 0.5,
            color: `rgba(74, 158, 255, ${Math.random() * 0.5})`
        });
    }
}

function drawParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.fill();
        
        // Mover partículas
        p.x += p.speedX;
        p.y += p.speedY;
        
        // Rebotar en bordes
        if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
        if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;
    }
    
    requestAnimationFrame(drawParticles);
}

// Inicializar
resizeCanvas();
createParticles();
drawParticles();

window.addEventListener('resize', function() {
    resizeCanvas();
    particles = [];
    createParticles();
});

// Asegurar que el canvas de partículas no bloquee el scroll y se quede de fondo
const canvasElement = document.getElementById('particles-canvas');
if (canvasElement) {
    canvasElement.style.position = 'fixed';
    canvasElement.style.top = '0';
    canvasElement.style.left = '0';
    canvasElement.style.zIndex = '-1'; // Ponerlo detrás de todo
    canvasElement.style.pointerEvents = 'none'; // Permitir hacer click en gráficos
}