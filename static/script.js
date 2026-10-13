/**
 * SMART CAMPUS MAINTENANCE REQUEST SYSTEM
 * Interactive Client-Side JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-dismiss flash alerts or manual close
    initAlerts();

    // 2. Request ID Copy to Clipboard Helper
    initCopyButtons();

    // 3. Admin Table Live Search & Filter
    initAdminFilter();

    // 4. Form Submission Feedback
    initFormValidation();
});

/**
 * Handle alert dismiss buttons
 */
function initAlerts() {
    const closeButtons = document.querySelectorAll('.alert-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.25s ease';
                setTimeout(() => alert.remove(), 250);
            }
        });
    });

    // Automatically fade out success alerts after 5 seconds
    const autoAlerts = document.querySelectorAll('.alert-success');
    autoAlerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentElement) {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.5s ease';
                setTimeout(() => alert.remove(), 500);
            }
        }, 5000);
    });
}

/**
 * Copy Request ID to clipboard with visual feedback
 */
function initCopyButtons() {
    const copyBtns = document.querySelectorAll('.btn-copy-id');
    copyBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const idText = this.getAttribute('data-id');
            if (!idText) return;

            navigator.clipboard.writeText(idText).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '✓ Copied!';
                this.classList.add('btn-copied');
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-copied');
                }, 2000);
            }).catch(err => {
                console.error('Clipboard copy failed:', err);
            });
        });
    });
}

/**
 * Client-side real-time filtering for Admin Dashboard table
 */
function initAdminFilter() {
    const searchInput = document.getElementById('tableSearchInput');
    const tableBody = document.getElementById('adminTableBody');

    if (!searchInput || !tableBody) return;

    searchInput.addEventListener('input', function () {
        const query = this.value.toLowerCase().trim();
        const rows = tableBody.querySelectorAll('tr.request-row');

        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            if (text.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

/**
 * Enhanced form submit validation and double-submission protection
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = 'Submitting...';
            }
        });
    });
}
