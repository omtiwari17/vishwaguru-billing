// Vishwaguru Ki Jhalak - Modern Desk Utilities & Shortcuts
// Keyboard navigation, clipboard copying, and HTMX feedback shimmers.

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initKeyboardShortcuts();
        initClipboardHelpers();
        initHtmxProgressIndicators();
        initDropdownDismissal();
    });

    // 1. Global Keyboard Shortcuts (Linear-grade desk productivity)
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function (e) {
            // Ignore if user is currently typing in an input, textarea, or select
            const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
            const isTyping = activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select' || (document.activeElement && document.activeElement.isContentEditable);

            // Command / Ctrl + K or '/' focuses main search input
            if ((e.key === '/' && !isTyping) || ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K'))) {
                e.preventDefault();
                const searchInput = document.querySelector('input[name="q"], input[type="search"]');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
                return;
            }

            // 'Escape' clears active search input and blurs
            if (e.key === 'Escape' && isTyping) {
                if (document.activeElement && (document.activeElement.name === 'q' || document.activeElement.type === 'search')) {
                    document.activeElement.value = '';
                    // trigger change for HTMX
                    document.activeElement.dispatchEvent(new Event('search'));
                    document.activeElement.blur();
                }
                return;
            }

            // 'N' navigates to New Bill creation if not typing
            if ((e.key === 'n' || e.key === 'N') && !isTyping && !e.ctrlKey && !e.metaKey && !e.altKey) {
                const newBillLink = document.querySelector('a[href*="/bills/new/"], a.btn-desk-primary[href*="bill"]');
                if (newBillLink && newBillLink.href) {
                    e.preventDefault();
                    window.location.href = newBillLink.href;
                }
                return;
            }
        });
    }

    // 2. Modern Clipboard Copying with Visual Feedback
    function initClipboardHelpers() {
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('[data-copy], [data-copy-value]');
            if (!btn) return;

            const textToCopy = btn.getAttribute('data-copy') || btn.getAttribute('data-copy-value');
            if (!textToCopy) return;

            e.preventDefault();
            navigator.clipboard.writeText(textToCopy).then(function () {
                const originalHtml = btn.innerHTML;
                const copiedLabel = btn.getAttribute('data-copied-text') || 'Copied!';
                btn.innerHTML = '<i class="bi bi-check2 text-paid" style="color: #15803d;"></i> <span style="color: #15803d;">' + copiedLabel + '</span>';
                btn.classList.add('copy-success');

                setTimeout(function () {
                    btn.innerHTML = originalHtml;
                    btn.classList.remove('copy-success');
                }, 2000);
            }).catch(function (err) {
                console.error('Clipboard copy failed:', err);
            });
        });
    }

    // 3. HTMX Progress Indicator & Request Polish
    function initHtmxProgressIndicators() {
        document.addEventListener('htmx:beforeRequest', function (e) {
            const target = e.detail.target;
            if (target) {
                target.classList.add('htmx-loading');
                const panel = target.closest('.bills-desk-panel, .desk-panel');
                if (panel) {
                    const shimmer = panel.querySelector('.desk-shimmer-bar');
                    if (shimmer) shimmer.style.opacity = '1';
                }
            }
        });

        document.addEventListener('htmx:afterRequest', function (e) {
            const target = e.detail.target;
            if (target) {
                target.classList.remove('htmx-loading');
                const panel = target.closest('.bills-desk-panel, .desk-panel');
                if (panel) {
                    const shimmer = panel.querySelector('.desk-shimmer-bar');
                    if (shimmer) shimmer.style.opacity = '0';
                }
            }
        });
    }


    // 4. Dropdown Menu Outside-Click & Single-Open Dismissal
    function initDropdownDismissal() {
        // Close on clicking anywhere outside
        document.addEventListener('click', function (e) {
            document.querySelectorAll('details.desk-menu-dropdown[open]').forEach(function (d) {
                if (!d.contains(e.target)) {
                    d.removeAttribute('open');
                }
            });
        });

        // Close on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('details.desk-menu-dropdown[open]').forEach(function (d) {
                    d.removeAttribute('open');
                });
            }
        });

        // When one menu opens, close any other open menu
        document.addEventListener('toggle', function (e) {
            if (e.target && e.target.matches && e.target.matches('details.desk-menu-dropdown[open]')) {
                document.querySelectorAll('details.desk-menu-dropdown[open]').forEach(function (d) {
                    if (d !== e.target) {
                        d.removeAttribute('open');
                    }
                });
            }
        }, true);
    }

})();
