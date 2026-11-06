// Vishwaguru Ad Billing - Live POS Interactivity & Sticky Receipt Synchronization

document.addEventListener('DOMContentLoaded', function () {
    window.siteLang = window.siteLang || document.documentElement.lang || 'en';
    // Form elements
    const baseInput = document.getElementById('id_base_amount');
    const discountInput = document.getElementById('id_discount_amount');
    const previousDueInput = document.getElementById('id_previous_due');
    const placementSelect = document.getElementById('id_placement_type');
    const customSizeInput = document.getElementById('id_custom_size_text');
    const customSizeContainer = document.getElementById('custom_size_container');
    const paymentStatusSelect = document.getElementById('id_payment_status');
    const amountPaidInput = document.getElementById('id_amount_paid');
    const paymentMethodSelect = document.getElementById('id_payment_method');
    const clientNameInput = document.getElementById('id_client_name');
    const clientPhoneInput = document.getElementById('id_client_phone');
    const clientAddressInput = document.getElementById('id_client_address');
    const clientGstinInput = document.getElementById('id_client_gstin');
    const clientSuggestionsBox = document.getElementById('client_suggestions_box');
    const clientPendingAlert = document.getElementById('client_pending_alert');
    const clientPendingAmountBadge = document.getElementById('client_pending_amount_badge');
    const btnAddPendingDue = document.getElementById('btn_add_pending_due');
    const editionDateInput = document.getElementById('id_edition_date');
    const billLangSelect = document.getElementById('id_bill_language');
    const receiptLangSelect = document.getElementById('receipt_bill_language');

    // Sticky Receipt live display elements
    const receiptClient = document.getElementById('receipt_client');
    const receiptPlacement = document.getElementById('receipt_placement');
    const receiptDate = document.getElementById('receipt_date');
    const receiptBase = document.getElementById('receipt_base');
    const receiptDiscountRow = document.getElementById('receipt_discount_row');
    const receiptDiscount = document.getElementById('receipt_discount');
    const receiptPreviousDueRow = document.getElementById('receipt_previous_due_row');
    const receiptPreviousDue = document.getElementById('receipt_previous_due');
    const receiptTotal = document.getElementById('receipt_total');
    const receiptStatusBadge = document.getElementById('receipt_status_badge');
    const receiptPaidRow = document.getElementById('receipt_paid_row');
    const receiptPaid = document.getElementById('receipt_paid');
    const receiptBalance = document.getElementById('receipt_balance');
    const partialAmountContainer = document.getElementById('partial_amount_container');

    // Currency Formatter
    function formatINR(amount) {
        return '₹' + Number(amount || 0).toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // 1. Calculate & Sync All Financials
    function calculateTotal() {
        const base = parseFloat(baseInput?.value) || 0;
        const discount = parseFloat(discountInput?.value) || 0;
        const previousDue = parseFloat(previousDueInput?.value) || 0;
        const netTotal = Math.max(0, (base - discount) + previousDue);
        const status = paymentStatusSelect ? paymentStatusSelect.value : 'Paid';

        // Auto-fill amount_paid if Paid or Unpaid
        if (paymentStatusSelect && amountPaidInput) {
            if (status === 'Paid') {
                amountPaidInput.value = netTotal.toFixed(2);
            } else if (status === 'Unpaid') {
                amountPaidInput.value = '0.00';
            }
        }

        const paid = parseFloat(amountPaidInput?.value) || 0;
        const balance = Math.max(0, netTotal - paid);

        // Update Sticky Receipt
        if (receiptBase) receiptBase.textContent = formatINR(base);
        if (receiptDiscountRow && receiptDiscount) {
            if (discount > 0) {
                receiptDiscountRow.style.display = 'flex';
                receiptDiscount.textContent = '- ' + formatINR(discount);
            } else {
                receiptDiscountRow.style.display = 'none';
            }
        }
        if (receiptPreviousDueRow && receiptPreviousDue) {
            if (previousDue > 0) {
                receiptPreviousDueRow.style.display = 'flex';
                receiptPreviousDue.textContent = '+ ' + formatINR(previousDue);
            } else {
                receiptPreviousDueRow.style.display = 'none';
            }
        }
        if (receiptTotal) receiptTotal.textContent = formatINR(netTotal);
        if (receiptPaid) receiptPaid.textContent = formatINR(paid);
        if (receiptBalance) receiptBalance.textContent = formatINR(balance);

        updateStatusBadge(status, balance);
    }

    // 2. Status Badge Sync
    function updateStatusBadge(status, balance) {
        if (!receiptStatusBadge) return;
        receiptStatusBadge.className = 'badge';
        if (status === 'Paid') {
            receiptStatusBadge.classList.add('badge-paid');
            receiptStatusBadge.innerHTML = '<i class="bi bi-check-circle-fill"></i> ' + (window.siteLang === 'hi' ? 'पूर्ण भुगतान' : 'Paid in Full');
            if (receiptPaidRow) receiptPaidRow.style.display = 'none';
        } else if (status === 'Partial') {
            receiptStatusBadge.classList.add('badge-partial');
            receiptStatusBadge.innerHTML = '<i class="bi bi-clock-history"></i> ' + (window.siteLang === 'hi' ? 'आंशिक' : 'Partial');
            if (receiptPaidRow) receiptPaidRow.style.display = 'flex';
        } else {
            receiptStatusBadge.classList.add('badge-unpaid');
            receiptStatusBadge.innerHTML = '<i class="bi bi-x-circle-fill"></i> ' + (window.siteLang === 'hi' ? 'अदत्त' : 'Unpaid');
            if (receiptPaidRow) receiptPaidRow.style.display = 'none';
        }
    }

    // 3. Client & Placement live receipt text
    function syncClientAndAdDetails() {
        if (receiptClient && clientNameInput) {
            const name = clientNameInput.value.trim();
            receiptClient.textContent = name || (window.siteLang === 'hi' ? 'ग्राहक का नाम' : 'Client Name');
        }
        if (receiptPlacement && placementSelect) {
            const selectedText = placementSelect.options[placementSelect.selectedIndex]?.text || '';
            receiptPlacement.textContent = selectedText || '---';
        }
        if (receiptDate && editionDateInput) {
            const dateVal = editionDateInput.value;
            if (dateVal) {
                const parts = dateVal.split('-');
                if (parts.length === 3) {
                    receiptDate.textContent = `${parts[2]}/${parts[1]}/${parts[0]}`;
                } else {
                    receiptDate.textContent = dateVal;
                }
            }
        }
    }

    // 4. Custom Size Visibility Toggle
    function toggleCustomSize() {
        if (!placementSelect || !customSizeContainer) return;
        const isCustom = placementSelect.value === 'Custom Size';
        if (isCustom) {
            customSizeContainer.style.display = 'flex';
            if (customSizeInput) customSizeInput.required = true;
        } else {
            customSizeContainer.style.display = 'none';
            if (customSizeInput) {
                customSizeInput.required = false;
                customSizeInput.value = '';
            }
        }
    }

    // 5. Preset Chips Setup for Placement
    const chipButtons = document.querySelectorAll('.chip-btn');
    chipButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const targetVal = this.dataset.value;
            if (placementSelect) {
                placementSelect.value = targetVal;
                // Trigger change
                placementSelect.dispatchEvent(new Event('change'));
            }
            chipButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Sync active chip if placement dropdown changes directly
    if (placementSelect) {
        placementSelect.addEventListener('change', function () {
            const currentVal = this.value;
            chipButtons.forEach(b => {
                if (b.dataset.value === currentVal) {
                    b.classList.add('active');
                } else {
                    b.classList.remove('active');
                }
            });
            toggleCustomSize();
            syncClientAndAdDetails();
        });
    }

    // 6. Payment Status Pills
    const statusPills = document.querySelectorAll('.pill-choice[data-status]');
    statusPills.forEach(pill => {
        pill.addEventListener('click', function () {
            const targetStatus = this.dataset.status;
            if (paymentStatusSelect) {
                paymentStatusSelect.value = targetStatus;
                paymentStatusSelect.dispatchEvent(new Event('change'));
            }
            updateStatusPillUI(targetStatus);
        });
    });

    function updateStatusPillUI(status) {
        statusPills.forEach(p => {
            p.classList.remove('active-paid', 'active-unpaid', 'active-partial');
            if (p.dataset.status === status) {
                if (status === 'Paid') p.classList.add('active-paid');
                else if (status === 'Unpaid') p.classList.add('active-unpaid');
                else if (status === 'Partial') p.classList.add('active-partial');
            }
        });

        if (partialAmountContainer) {
            partialAmountContainer.style.display = status === 'Partial' ? 'block' : 'none';
        }
    }

    if (paymentStatusSelect) {
        paymentStatusSelect.addEventListener('change', function () {
            updateStatusPillUI(this.value);
            calculateTotal();
        });
    }

    // 7. Payment Method Pills
    const methodPills = document.querySelectorAll('.pill-choice[data-method]');
    methodPills.forEach(pill => {
        pill.addEventListener('click', function () {
            const targetMethod = this.dataset.method;
            if (paymentMethodSelect) {
                paymentMethodSelect.value = targetMethod;
                paymentMethodSelect.dispatchEvent(new Event('change'));
            }
            methodPills.forEach(m => m.classList.remove('active-method'));
            this.classList.add('active-method');
        });
    });

    if (paymentMethodSelect) {
        paymentMethodSelect.addEventListener('change', function () {
            const currentMethod = this.value;
            methodPills.forEach(m => {
                if (m.dataset.method === currentMethod) {
                    m.classList.add('active-method');
                } else {
                    m.classList.remove('active-method');
                }
            });
        });
    }

    // 8. Quick Date Buttons
    const dateBtns = document.querySelectorAll('.date-btn[data-offset]');
    dateBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const offset = parseInt(this.dataset.offset, 10) || 0;
            const d = new Date();
            d.setDate(d.getDate() + offset);
            const yyyy = d.getFullYear();
            const mm = String(d.getMonth() + 1).padStart(2, '0');
            const dd = String(d.getDate()).padStart(2, '0');
            if (editionDateInput) {
                editionDateInput.value = `${yyyy}-${mm}-${dd}`;
                editionDateInput.dispatchEvent(new Event('input'));
            }
        });
    });

    // 9. Synchronize Receipt Language dropdown with main form
    if (receiptLangSelect && billLangSelect) {
        receiptLangSelect.value = billLangSelect.value;
        receiptLangSelect.addEventListener('change', function () {
            billLangSelect.value = this.value;
        });
        billLangSelect.addEventListener('change', function () {
            receiptLangSelect.value = this.value;
        });
    }

    // Helper: Parse composite "हिन्दी (English)" string according to active site language
    function parseBilingualString(str) {
        if (!str) return { primary: '', secondary: '' };
        const m = str.match(/^(.*?)\s*\((.*?)\)$/);
        if (m) {
            const p1 = m[1].trim();
            const p2 = m[2].trim();
            const p1IsHi = /[\u0900-\u097F]/.test(p1);
            if (window.siteLang === 'hi') {
                return p1IsHi ? { primary: p1, secondary: p2 } : { primary: p2, secondary: p1 };
            } else {
                return p1IsHi ? { primary: p2, secondary: p1 } : { primary: p1, secondary: p2 };
            }
        }
        return { primary: str.trim(), secondary: '' };
    }

    // 10. Live Real-Time Auto-Translation Counterparts
    function setupLiveTranslation(sourceInputId, transInputId, btnSyncId, lblId) {
        const sourceInput = document.getElementById(sourceInputId);
        const transInput = document.getElementById(transInputId);
        const btnSync = document.getElementById(btnSyncId);
        const lbl = document.getElementById(lblId);

        if (!sourceInput || !transInput) return null;

        let debounceTimer = null;
        let isManuallyEdited = false;

        transInput.addEventListener('input', function () {
            isManuallyEdited = true;
        });

        function performTranslation(force) {
            const text = sourceInput.value.trim();
            if (!text) {
                if (!isManuallyEdited || force) {
                    transInput.value = '';
                }
                return;
            }

            if (isManuallyEdited && !force && transInput.value.trim() !== '') {
                return;
            }

            if (btnSync) {
                btnSync.innerHTML = '<i class="bi bi-hourglass-split"></i>';
                btnSync.disabled = true;
            }

            fetch('/bills/api/translate/?text=' + encodeURIComponent(text))
                .then(res => res.json())
                .then(data => {
                    if (data && data.translated) {
                        transInput.value = data.translated;
                        isManuallyEdited = false;
                        if (lbl) {
                            if (data.detected_script === 'hi') {
                                lbl.innerHTML = '<i class="bi bi-translate"></i> ' + (window.siteLang === 'hi' ? 'अंग्रेजी अनुवाद:' : 'English Trans:');
                            } else {
                                lbl.innerHTML = '<i class="bi bi-translate"></i> ' + (window.siteLang === 'hi' ? 'हिन्दी अनुवाद:' : 'Hindi Trans:');
                            }
                        }
                    }
                })
                .catch(err => {
                    console.error('Translation error:', err);
                })
                .finally(() => {
                    if (btnSync) {
                        btnSync.innerHTML = '<i class="bi bi-arrow-repeat"></i>';
                        btnSync.disabled = false;
                    }
                });
        }

        sourceInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                performTranslation(false);
            }, 450);
        });

        sourceInput.addEventListener('blur', function () {
            clearTimeout(debounceTimer);
            if (!transInput.value.trim()) {
                performTranslation(false);
            }
        });

        if (btnSync) {
            btnSync.addEventListener('click', function () {
                performTranslation(true);
            });
        }

        return {
            trigger: function (force) {
                performTranslation(force === undefined ? true : force);
            }
        };
    }

    const nameTransCtrl = setupLiveTranslation('id_client_name', 'id_client_name_trans', 'btn_sync_client_name', 'lbl_client_name_trans');
    const addrTransCtrl = setupLiveTranslation('id_client_address', 'id_client_address_trans', 'btn_sync_client_address', 'lbl_client_address_trans');
    const adTitleTransCtrl = setupLiveTranslation('id_ad_title', 'id_ad_title_trans', 'btn_sync_ad_title', 'lbl_ad_title_trans');

    // 10. Client Autocomplete & Recall Past Clients
    let searchDebounceTimer = null;
    let detectedPendingDue = 0;

    if (clientNameInput && clientSuggestionsBox) {
        clientNameInput.addEventListener('input', function () {
            const query = this.value.trim();
            clearTimeout(searchDebounceTimer);

            if (query.length < 1) {
                clientSuggestionsBox.style.display = 'none';
                clientSuggestionsBox.innerHTML = '';
                return;
            }

            searchDebounceTimer = setTimeout(function () {
                fetch('/bills/api/clients/search/?q=' + encodeURIComponent(query))
                    .then(response => response.json())
                    .then(data => {
                        const clients = data.clients || [];
                        if (clients.length === 0) {
                            clientSuggestionsBox.style.display = 'none';
                            clientSuggestionsBox.innerHTML = '';
                            return;
                        }

                        clientSuggestionsBox.innerHTML = '';
                        clients.forEach(c => {
                            const item = document.createElement('div');
                            item.className = 'client-suggestion-item';

                            let dueBadgeHtml = '';
                            if (c.pending_due > 0) {
                                dueBadgeHtml = `<span class="suggestion-due-badge"><i class="bi bi-clock-history"></i> बकाया: ${formatINR(c.pending_due)}</span>`;
                            }

                            item.innerHTML = `
                                <div>
                                    <div class="suggestion-name">${c.name}</div>
                                    <div class="suggestion-phone"><i class="bi bi-telephone"></i> ${c.phone || (window.siteLang === 'hi' ? 'फ़ोन नहीं' : 'No Phone')} ${c.address ? '• ' + c.address.substring(0, 30) : ''}</div>
                                </div>
                                ${dueBadgeHtml}
                            `;

                            item.addEventListener('click', function () {
                                // Auto-fill remembered client fields with intelligent bilingual splitting
                                const parsedName = parseBilingualString(c.name);
                                clientNameInput.value = parsedName.primary;
                                const clientNameTrans = document.getElementById('id_client_name_trans');
                                if (clientNameTrans) {
                                    clientNameTrans.value = parsedName.secondary;
                                    if (!parsedName.secondary) {
                                        nameTransCtrl?.trigger(true);
                                    }
                                }

                                if (clientPhoneInput) clientPhoneInput.value = c.phone || '';

                                const parsedAddr = parseBilingualString(c.address || '');
                                if (clientAddressInput) {
                                    clientAddressInput.value = parsedAddr.primary;
                                    const clientAddrTrans = document.getElementById('id_client_address_trans');
                                    if (clientAddrTrans) {
                                        clientAddrTrans.value = parsedAddr.secondary;
                                        if (!parsedAddr.secondary && parsedAddr.primary) {
                                            addrTransCtrl?.trigger(true);
                                        }
                                    }
                                }

                                if (clientGstinInput) clientGstinInput.value = c.gstin || '';

                                // Sync client name to receipt
                                syncClientAndAdDetails();

                                // Check pending due from past bills
                                detectedPendingDue = c.pending_due || 0;
                                if (detectedPendingDue > 0 && clientPendingAlert && clientPendingAmountBadge) {
                                    clientPendingAmountBadge.textContent = formatINR(detectedPendingDue);
                                    clientPendingAlert.style.display = 'block';
                                } else if (clientPendingAlert) {
                                    clientPendingAlert.style.display = 'none';
                                }

                                clientSuggestionsBox.style.display = 'none';
                            });

                            clientSuggestionsBox.appendChild(item);
                        });

                        clientSuggestionsBox.style.display = 'block';
                    })
                    .catch(err => {
                        console.error('Error fetching client suggestions:', err);
                    });
            }, 250);
        });

        // Hide suggestions on outside click
        document.addEventListener('click', function (e) {
            if (!clientNameInput.contains(e.target) && !clientSuggestionsBox.contains(e.target)) {
                clientSuggestionsBox.style.display = 'none';
            }
        });
    }

    // 1-Click Add Pending Due Button
    if (btnAddPendingDue && previousDueInput) {
        btnAddPendingDue.addEventListener('click', function () {
            if (detectedPendingDue > 0) {
                previousDueInput.value = detectedPendingDue.toFixed(2);
                calculateTotal();
                if (clientPendingAlert) {
                    clientPendingAlert.style.display = 'none';
                }
            }
        });
    }

    // Attach Input Event Listeners
    if (baseInput) baseInput.addEventListener('input', calculateTotal);
    if (discountInput) discountInput.addEventListener('input', calculateTotal);
    if (previousDueInput) previousDueInput.addEventListener('input', calculateTotal);
    if (amountPaidInput) amountPaidInput.addEventListener('input', calculateTotal);
    if (clientNameInput) clientNameInput.addEventListener('input', syncClientAndAdDetails);
    if (editionDateInput) editionDateInput.addEventListener('input', syncClientAndAdDetails);

    // Duplicate submission prevention & progress feedback
    const submitBtn = document.getElementById('submitBillBtn');
    if (submitBtn) {
        const form = submitBtn.closest('form');
        if (form) {
            form.addEventListener('submit', function () {
                if (!form.checkValidity || form.checkValidity()) {
                    submitBtn.disabled = true;
                    submitBtn.style.opacity = '0.75';
                    submitBtn.style.cursor = 'wait';
                    submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> ' + (document.documentElement.lang === 'hi' ? 'बिल सुरक्षित हो रहा है...' : 'Generating Bill...');
                }
            });
        }
    }

    // Initial setup on page load
    toggleCustomSize();
    if (paymentStatusSelect) updateStatusPillUI(paymentStatusSelect.value);
    syncClientAndAdDetails();
    calculateTotal();
});
