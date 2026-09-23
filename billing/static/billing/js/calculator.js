// Vishwaguru Ad Billing - Live Amount Calculator & Form Interactivity

document.addEventListener('DOMContentLoaded', function () {
    const baseInput = document.getElementById('id_base_amount');
    const discountInput = document.getElementById('id_discount_amount');
    const placementSelect = document.getElementById('id_placement_type');
    const customSizeInput = document.getElementById('id_custom_size_text');
    const customSizeGroup = customSizeInput ? customSizeInput.closest('.form-group') : null;
    const paymentStatusSelect = document.getElementById('id_payment_status');
    const amountPaidInput = document.getElementById('id_amount_paid');
    const liveTotalDisplay = document.getElementById('live_total_display');
    const liveBalanceDisplay = document.getElementById('live_balance_display');

    function calculateTotal() {
        const base = parseFloat(baseInput?.value) || 0;
        const discount = parseFloat(discountInput?.value) || 0;
        const netTotal = Math.max(0, base - discount);

        if (liveTotalDisplay) {
            liveTotalDisplay.textContent = '₹' + netTotal.toLocaleString('en-IN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }

        // Auto update amount_paid if status is Paid
        if (paymentStatusSelect && paymentStatusSelect.value === 'Paid' && amountPaidInput) {
            amountPaidInput.value = netTotal.toFixed(2);
        }

        calculateBalance(netTotal);
    }

    function calculateBalance(currentTotal) {
        if (!liveBalanceDisplay) return;
        const netTotal = currentTotal !== undefined ? currentTotal : Math.max(0, (parseFloat(baseInput?.value) || 0) - (parseFloat(discountInput?.value) || 0));
        const paid = parseFloat(amountPaidInput?.value) || 0;
        const balance = Math.max(0, netTotal - paid);

        liveBalanceDisplay.textContent = '₹' + balance.toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    function toggleCustomSize() {
        if (!placementSelect || !customSizeGroup) return;
        const isCustom = placementSelect.value === 'Custom Size';
        if (isCustom) {
            customSizeGroup.style.display = 'flex';
            customSizeInput.required = true;
        } else {
            customSizeGroup.style.display = 'none';
            customSizeInput.required = false;
        }
    }

    // Attach listeners
    if (baseInput) baseInput.addEventListener('input', calculateTotal);
    if (discountInput) discountInput.addEventListener('input', calculateTotal);
    if (amountPaidInput) amountPaidInput.addEventListener('input', () => calculateBalance());

    if (placementSelect) {
        placementSelect.addEventListener('change', toggleCustomSize);
        toggleCustomSize(); // Run on initial page load
    }

    if (paymentStatusSelect) {
        paymentStatusSelect.addEventListener('change', function () {
            const netTotal = Math.max(0, (parseFloat(baseInput?.value) || 0) - (parseFloat(discountInput?.value) || 0));
            if (this.value === 'Paid' && amountPaidInput) {
                amountPaidInput.value = netTotal.toFixed(2);
            } else if (this.value === 'Unpaid' && amountPaidInput) {
                amountPaidInput.value = '0.00';
            }
            calculateBalance(netTotal);
        });
    }

    // Initial calculation on load
    calculateTotal();
});
