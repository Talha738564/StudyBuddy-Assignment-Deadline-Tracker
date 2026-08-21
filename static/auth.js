document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-password-toggle]').forEach((toggle) => {
        const input = document.getElementById(toggle.dataset.passwordToggle);
        if (!input) return;

        toggle.addEventListener('click', () => {
            const isVisible = input.type === 'text';
            input.type = isVisible ? 'password' : 'text';
            toggle.setAttribute('aria-label', isVisible ? 'Show password' : 'Hide password');
            toggle.setAttribute('aria-pressed', String(!isVisible));
        });
    });

    document.querySelectorAll('.auth-transition-link').forEach((link) => {
        link.addEventListener('click', (event) => {
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
            event.preventDefault();
            document.querySelector('.auth-panel')?.classList.add('auth-leaving');
            window.setTimeout(() => { window.location.href = link.href; }, 260);
        });
    });
});