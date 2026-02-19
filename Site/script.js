/* ========================================
   SlickClick Landing Page — Interactions
   ======================================== */

// --- Particle Background ---
(function initParticles() {
    const canvas = document.getElementById('particles');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let w, h;
    let animId;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    function createParticles() {
        particles = [];
        const count = Math.floor((w * h) / 18000);
        for (let i = 0; i < count; i++) {
            particles.push({
                x: Math.random() * w,
                y: Math.random() * h,
                r: Math.random() * 1.5 + 0.3,
                dx: (Math.random() - 0.5) * 0.3,
                dy: (Math.random() - 0.5) * 0.3,
                alpha: Math.random() * 0.4 + 0.1,
            });
        }
    }

    function draw() {
        ctx.clearRect(0, 0, w, h);
        for (const p of particles) {
            p.x += p.dx;
            p.y += p.dy;
            if (p.x < 0) p.x = w;
            if (p.x > w) p.x = 0;
            if (p.y < 0) p.y = h;
            if (p.y > h) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(233, 69, 96, ${p.alpha})`;
            ctx.fill();
        }

        // Draw connections
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(233, 69, 96, ${0.06 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }

        animId = requestAnimationFrame(draw);
    }

    resize();
    createParticles();
    draw();

    window.addEventListener('resize', () => {
        resize();
        createParticles();
    });
})();

// --- Navbar Scroll Effect ---
(function initNav() {
    const nav = document.getElementById('navbar');
    if (!nav) return;

    function onScroll() {
        if (window.scrollY > 40) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
})();

// --- Mobile Menu ---
const navToggle = document.getElementById('navToggle');
const mobileMenu = document.getElementById('mobileMenu');

if (navToggle && mobileMenu) {
    navToggle.addEventListener('click', () => {
        mobileMenu.classList.toggle('open');
        document.body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
    });
}

function closeMobile() {
    if (mobileMenu) {
        mobileMenu.classList.remove('open');
        document.body.style.overflow = '';
    }
}

// --- Scroll Reveal ---
(function initScrollReveal() {
    const els = document.querySelectorAll('.fade-in');
    if (!els.length) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
    );

    els.forEach((el) => observer.observe(el));
})();

// --- Interactive Mockup Demo ---
(function initMockupDemo() {
    const btn = document.getElementById('mockupBtn');
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    const counter = document.getElementById('clickCounter');
    const msDisplay = document.getElementById('mockupMs');

    if (!btn || !dot || !text || !counter) return;

    let running = false;
    let clicks = 0;
    let interval = null;

    btn.addEventListener('click', () => {
        running = !running;

        if (running) {
            btn.textContent = '■ Stop';
            btn.classList.add('running');
            dot.classList.add('running');
            text.textContent = 'Running';
            clicks = 0;

            interval = setInterval(() => {
                clicks++;
                counter.textContent = `Clicks: ${clicks.toLocaleString()}`;
                // Animate the ms value slightly
                if (msDisplay) {
                    msDisplay.style.transform = 'scale(1.08)';
                    setTimeout(() => {
                        msDisplay.style.transform = 'scale(1)';
                    }, 50);
                }
            }, 80);
        } else {
            btn.textContent = '▶ Start';
            btn.classList.remove('running');
            dot.classList.remove('running');
            text.textContent = 'Stopped';
            clearInterval(interval);
        }
    });
})();

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// --- Cookie Consent Banner ---
(function initCookieBanner() {
    const banner = document.getElementById('cookieBanner');
    const acceptBtn = document.getElementById('cookieAccept');
    const declineBtn = document.getElementById('cookieDecline');

    if (!banner) return;

    // Check if user already made a choice
    const consent = localStorage.getItem('slickclick_cookie_consent');
    if (consent) {
        banner.classList.add('hidden');
        return;
    }

    function dismiss(choice) {
        localStorage.setItem('slickclick_cookie_consent', choice);
        banner.classList.add('hidden');
        // Remove from DOM after animation
        setTimeout(() => banner.remove(), 500);
    }

    if (acceptBtn) acceptBtn.addEventListener('click', () => dismiss('accepted'));
    if (declineBtn) declineBtn.addEventListener('click', () => dismiss('declined'));
})();
