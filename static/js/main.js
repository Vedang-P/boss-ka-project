/* ============================================================
   Academic Aggregator — main.js
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initCounters();
    initWorkloadBars();
    initFadeUp();
    initMessages();
});

/* ── Sidebar Mobile Toggle ── */
function initSidebar() {
    const sidebar   = document.getElementById('sidebar');
    const overlay   = document.getElementById('sidebar-overlay');
    const hamburger = document.getElementById('hamburger');

    if (!sidebar || !hamburger) return;

    function openSidebar() {
        sidebar.classList.add('open');
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
        document.body.style.overflow = '';
    }

    hamburger.addEventListener('click', openSidebar);
    overlay.addEventListener('click', closeSidebar);

    // Close when nav item clicked on mobile
    sidebar.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            if (window.innerWidth <= 768) closeSidebar();
        });
    });
}

/* ── Animated Stat Counters ── */
function animateCounter(el) {
    const target   = parseFloat(el.dataset.counter);
    const suffix   = el.dataset.counterSuffix   || '';
    const decimals = parseInt(el.dataset.counterDecimals || '0', 10);
    const duration = 1400;
    const start    = performance.now();

    function step(now) {
        const elapsed  = now - start;
        const progress = Math.min(elapsed / duration, 1);
        // Ease-out cubic
        const eased    = 1 - Math.pow(1 - progress, 3);
        const current  = (target * eased).toFixed(decimals);
        el.textContent = current + suffix;
        if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
}

function initCounters() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.counted) {
                entry.target.dataset.counted = 'true';
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('[data-counter]').forEach(el => observer.observe(el));
}

/* ── Workload Bar Animations ── */
function initWorkloadBars() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const fill = entry.target;
                // Defer one frame so the CSS transition fires
                requestAnimationFrame(() => {
                    fill.style.width = (fill.dataset.width || '0') + '%';
                });
                observer.unobserve(fill);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.workload-fill').forEach(el => observer.observe(el));
}

/* ── Scroll Fade-In ── */
function initFadeUp() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });

    document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));
}

/* ── Message Auto-Dismiss ── */
function initMessages() {
    document.querySelectorAll('.message').forEach(msg => {
        // Inject dismiss button
        const btn = document.createElement('button');
        btn.className = 'message-dismiss';
        btn.innerHTML = '&times;';
        btn.setAttribute('aria-label', 'Dismiss');

        function dismiss() {
            msg.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
            msg.style.opacity    = '0';
            msg.style.transform  = 'translateX(16px)';
            setTimeout(() => msg.remove(), 350);
        }

        btn.addEventListener('click', dismiss);
        msg.appendChild(btn);

        // Auto-dismiss after 6 seconds
        setTimeout(dismiss, 6000);
    });
}
