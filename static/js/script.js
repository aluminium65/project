document.addEventListener('DOMContentLoaded', () => {
    const candidates = document.querySelectorAll('.vote-row img');
    candidates.forEach(img => {
        img.addEventListener('click', () => {
            const row = img.parentElement;
            row.querySelectorAll('img').forEach(i => i.style.border = '3px solid transparent');
            img.style.border = '3px solid #28a745';

            // Optional: set a hidden input value if you use one
            const input = row.querySelector('input[type="hidden"]');
            if (input) input.value = img.dataset.candidate;
        });
    });
});
