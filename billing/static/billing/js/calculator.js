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
    const clientNameTransInput = document.getElementById('id_client_name_trans');
    const clientAddressTransInput = document.getElementById('id_client_address_trans');
    const adTitleTransInput = document.getElementById('id_ad_title_trans');
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

    // Bilingual Localization Dictionary for Sticky Receipt
    const RECEIPT_I18N = {
        en: {
            title: 'Invoice Summary',
            mastheadTitle: 'Vishwaguru Ki Jhalak',
            mastheadSub: 'Vishwaguru Ki Jhalak Billing',
            lblClient: 'Client:',
            clientFallback: 'Client Name',
            lblPlacement: 'Placement:',
            placementFallback: 'Select Placement',
            lblDate: 'Edition Date:',
            lblBase: 'Base Rate:',
            lblDiscount: 'Discount:',
            lblPreviousDue: 'Previous Due:',
            lblTotal: 'Net Total:',
            lblStatus: 'Status:',
            lblPaid: 'Paid Now:',
            lblBalance: 'Balance Due:',
            btnSubmit: 'Generate Bill & Print',
            footerNote: 'Instant WeasyPrint PDF & WhatsApp link',
            statusPaid: 'Paid in Full',
            statusPartial: 'Partial',
            statusUnpaid: 'Unpaid',
            placements: {
                'Front Page Full': 'Front Page — Full Page',
                'Front Page Half': 'Front Page — Half Page',
                'Front Page Quarter': 'Front Page — Quarter (1/4)',
                'Inside Page Full': 'Inside Page — Full Page',
                'Inside Page Half': 'Inside Page — Half Page',
                'Inside Page Quarter': 'Inside Page — Quarter (1/4)',
                'Back Page Full': 'Back Page — Full Page',
                'Back Page Half': 'Back Page — Half Page',
                'Back Page Quarter': 'Back Page — Quarter (1/4)',
                'Ear Panel': 'Ear Panel (Top Header)',
                'Custom Size': 'Custom Dimensions'
            }
        },
        hi: {
            title: 'बिल सारांश',
            mastheadTitle: 'विश्वगुरु की झलक',
            mastheadSub: 'विश्वगुरु की झलक बिलिंग',
            lblClient: 'विज्ञापनदाता:',
            clientFallback: 'ग्राहक का नाम',
            lblPlacement: 'स्थान व आकार:',
            placementFallback: 'स्थान चुनें',
            lblDate: 'प्रकाशन दिनांक:',
            lblBase: 'मूल दर:',
            lblDiscount: 'छूट:',
            lblPreviousDue: 'पुराना बकाया:',
            lblTotal: 'शुद्ध देय राशि:',
            lblStatus: 'स्थिति:',
            lblPaid: 'प्राप्त राशि:',
            lblBalance: 'शेष देय राशि:',
            btnSubmit: 'बिल बनाएं व प्रिंट करें',
            footerNote: 'तुरंत वीज़ीप्रिंट पीडीएफ व व्हाट्सऐप लिंक',
            statusPaid: 'पूर्ण भुगतान',
            statusPartial: 'आंशिक भुगतान',
            statusUnpaid: 'अदत्त',
            placements: {
                'Front Page Full': 'मुख्य पृष्ठ — पूरा पेज',
                'Front Page Half': 'मुख्य पृष्ठ — आधा पेज',
                'Front Page Quarter': 'मुख्य पृष्ठ — चौथाई',
                'Inside Page Full': 'अंदर का पृष्ठ — पूरा पेज',
                'Inside Page Half': 'अंदर का पृष्ठ — आधा पेज',
                'Inside Page Quarter': 'अंदर का पृष्ठ — चौथाई',
                'Back Page Full': 'अंतिम पृष्ठ — पूरा पेज',
                'Back Page Half': 'अंतिम पृष्ठ — आधा पेज',
                'Back Page Quarter': 'अंतिम पृष्ठ — चौथाई',
                'Ear Panel': 'शीर्ष विज्ञापन (ईयर पैनल)',
                'Custom Size': 'विशिष्ट आकार'
            }
        },
        bi: {
            title: 'Invoice Summary / बिल सारांश',
            mastheadTitle: 'विश्वगुरु की झलक / Vishwaguru',
            mastheadSub: 'विश्वगुरु की झलक बिलिंग (Billing)',
            lblClient: 'Client / विज्ञापनदाता:',
            clientFallback: 'ग्राहक का नाम (Client)',
            lblPlacement: 'Placement / स्थान:',
            placementFallback: 'स्थान / Placement',
            lblDate: 'Date / दिनांक:',
            lblBase: 'Base / मूल दर:',
            lblDiscount: 'Discount / छूट:',
            lblPreviousDue: 'Old Due / पुराना बकाया:',
            lblTotal: 'Net Total / कुल देय:',
            lblStatus: 'Status / स्थिति:',
            lblPaid: 'Paid / प्राप्त:',
            lblBalance: 'Due / शेष बकाया:',
            btnSubmit: 'Generate Bill & Print / बिल बनाएं',
            footerNote: 'Instant WeasyPrint PDF & WhatsApp link',
            statusPaid: 'Paid in Full (पूर्ण भुगतान)',
            statusPartial: 'Partial (आंशिक)',
            statusUnpaid: 'Unpaid (अदत्त)',
            placements: {
                'Front Page Full': 'मुख्य पृष्ठ पूरा पेज (Front Full)',
                'Front Page Half': 'मुख्य पृष्ठ आधा पेज (Front Half)',
                'Front Page Quarter': 'मुख्य पृष्ठ चौथाई (Front Quarter)',
                'Inside Page Full': 'अंदर का पृष्ठ पूरा (Inside Full)',
                'Inside Page Half': 'अंदर का पृष्ठ आधा (Inside Half)',
                'Inside Page Quarter': 'अंदर का पृष्ठ चौथाई (Inside Quarter)',
                'Back Page Full': 'अंतिम पृष्ठ पूरा (Back Full)',
                'Back Page Half': 'अंतिम पृष्ठ आधा (Back Half)',
                'Back Page Quarter': 'अंतिम पृष्ठ चौथाई (Back Quarter)',
                'Ear Panel': 'शीर्ष विज्ञापन (Ear Panel)',
                'Custom Size': 'विशिष्ट आकार (Custom Size)'
            }
        }
    };

    // 2. Localize Sticky Receipt on Language Change
    function updateReceiptLanguage(targetLang) {
        const lang = targetLang || (receiptLangSelect ? receiptLangSelect.value : (billLangSelect ? billLangSelect.value : 'en'));
        const i18n = RECEIPT_I18N[lang] || RECEIPT_I18N.en;

        const cardTitle = document.getElementById('receipt_card_title');
        if (cardTitle) cardTitle.textContent = i18n.title;

        const mastTitle = document.getElementById('receipt_masthead_title');
        if (mastTitle) mastTitle.textContent = i18n.mastheadTitle;

        const mastSub = document.getElementById('receipt_masthead_sub');
        if (mastSub) mastSub.textContent = i18n.mastheadSub;

        const lblClient = document.getElementById('lbl_receipt_client');
        if (lblClient) lblClient.textContent = i18n.lblClient;

        const lblPlacement = document.getElementById('lbl_receipt_placement');
        if (lblPlacement) lblPlacement.textContent = i18n.lblPlacement;

        const lblDate = document.getElementById('lbl_receipt_date');
        if (lblDate) lblDate.textContent = i18n.lblDate;

        const lblBase = document.getElementById('lbl_receipt_base');
        if (lblBase) lblBase.textContent = i18n.lblBase;

        const lblDiscount = document.getElementById('lbl_receipt_discount');
        if (lblDiscount) lblDiscount.textContent = i18n.lblDiscount;

        const lblPreviousDue = document.getElementById('lbl_receipt_previous_due');
        if (lblPreviousDue) lblPreviousDue.textContent = i18n.lblPreviousDue;

        const lblTotal = document.getElementById('lbl_receipt_total');
        if (lblTotal) lblTotal.textContent = i18n.lblTotal;

        const lblStatus = document.getElementById('lbl_receipt_status');
        if (lblStatus) lblStatus.textContent = i18n.lblStatus;

        const lblPaid = document.getElementById('lbl_receipt_paid');
        if (lblPaid) lblPaid.textContent = i18n.lblPaid;

        const lblBalance = document.getElementById('lbl_receipt_balance');
        if (lblBalance) lblBalance.textContent = i18n.lblBalance;

        const btnSubmitText = document.getElementById('submitBillBtnText');
        if (btnSubmitText) btnSubmitText.textContent = i18n.btnSubmit;

        const footerNoteText = document.getElementById('receipt_footer_note_text');
        if (footerNoteText) footerNoteText.textContent = i18n.footerNote;

        // Re-sync client name, placement & status badge in this language
        syncClientAndAdDetails();
        const currentStatus = paymentStatusSelect ? paymentStatusSelect.value : 'Paid';
        const paid = parseFloat(amountPaidInput?.value) || 0;
        const base = parseFloat(baseInput?.value) || 0;
        const discount = parseFloat(discountInput?.value) || 0;
        const previousDue = parseFloat(previousDueInput?.value) || 0;
        const netTotal = Math.max(0, (base - discount) + previousDue);
        const balance = Math.max(0, netTotal - paid);
        updateStatusBadge(currentStatus, balance);
    }

    // 3. Status Badge Sync
    function updateStatusBadge(status, balance) {
        if (!receiptStatusBadge) return;
        const currentBillLang = receiptLangSelect ? receiptLangSelect.value : (billLangSelect?.value || 'en');
        const i18n = RECEIPT_I18N[currentBillLang] || RECEIPT_I18N.en;

        receiptStatusBadge.className = 'badge';
        if (status === 'Paid') {
            receiptStatusBadge.classList.add('badge-paid');
            receiptStatusBadge.innerHTML = '<i class="bi bi-check-circle-fill"></i> ' + i18n.statusPaid;
            if (receiptPaidRow) receiptPaidRow.style.display = 'none';
        } else if (status === 'Partial') {
            receiptStatusBadge.classList.add('badge-partial');
            receiptStatusBadge.innerHTML = '<i class="bi bi-clock-history"></i> ' + i18n.statusPartial;
            if (receiptPaidRow) receiptPaidRow.style.display = 'flex';
        } else {
            receiptStatusBadge.classList.add('badge-unpaid');
            receiptStatusBadge.innerHTML = '<i class="bi bi-x-circle-fill"></i> ' + i18n.statusUnpaid;
            if (receiptPaidRow) receiptPaidRow.style.display = 'none';
        }
    }

    // 4. Client & Placement live receipt text
    function syncClientAndAdDetails() {
        const currentBillLang = receiptLangSelect ? receiptLangSelect.value : (billLangSelect?.value || 'en');
        const i18n = RECEIPT_I18N[currentBillLang] || RECEIPT_I18N.en;

        // 1. Client Name
        if (receiptClient) {
            const rawPrimary = clientNameInput ? clientNameInput.value.trim() : '';
            const rawTrans = clientNameTransInput ? clientNameTransInput.value.trim() : '';

            let displayName = '';
            if (rawPrimary || rawTrans) {
                // Check if rawPrimary itself has composite "हिन्दी (English)" format
                const compMatch = rawPrimary.match(/^(.*?)\s*\((.*?)\)$/);
                let compHi = '', compEn = '';
                if (compMatch) {
                    const p1 = compMatch[1].trim();
                    const p2 = compMatch[2].trim();
                    if (/[ऀ-ॿ]/.test(p1)) {
                        compHi = p1; compEn = p2;
                    } else {
                        compHi = p2; compEn = p1;
                    }
                }

                // If not composite, check individual scripts of primary and trans
                const pIsHi = /[ऀ-ॿ]/.test(rawPrimary);
                const tIsHi = /[ऀ-ॿ]/.test(rawTrans);

                let hiName = compHi;
                let enName = compEn;

                if (!hiName) {
                    if (pIsHi) hiName = rawPrimary;
                    else if (tIsHi) hiName = rawTrans;
                }
                if (!enName) {
                    if (!pIsHi && rawPrimary) enName = rawPrimary;
                    else if (!tIsHi && rawTrans) enName = rawTrans;
                }

                if (currentBillLang === 'hi') {
                    displayName = hiName || enName || rawPrimary;
                } else if (currentBillLang === 'en') {
                    displayName = enName || hiName || rawPrimary;
                } else { // 'bi'
                    if (hiName && enName) {
                        displayName = `${hiName} (${enName})`;
                    } else {
                        displayName = rawPrimary || rawTrans;
                    }
                }
            }

            receiptClient.textContent = displayName || i18n.clientFallback;
        }

        // 2. Placement / Size Preset
        if (receiptPlacement && placementSelect) {
            const selectedVal = placementSelect.value;
            if (selectedVal === 'Custom Size') {
                const rawCustom = customSizeInput ? customSizeInput.value.trim() : '';
                if (rawCustom) {
                    if (currentBillLang === 'hi') {
                        receiptPlacement.textContent = rawCustom.replace(/(?:cm|cms|centimeters?)/gi, 'सेमी');
                    } else {
                        receiptPlacement.textContent = rawCustom.replace(/(?:सेमी|से\.मी\.)/g, 'cm');
                    }
                } else {
                    receiptPlacement.textContent = i18n.placements['Custom Size'] || 'Custom Size';
                }
            } else {
                const localizedPlacement = i18n.placements[selectedVal];
                if (localizedPlacement) {
                    receiptPlacement.textContent = localizedPlacement;
                } else {
                    const optionText = placementSelect.options[placementSelect.selectedIndex]?.text || '';
                    receiptPlacement.textContent = optionText || i18n.placementFallback;
                }
            }
        }

        // 3. Edition Date
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

    // 9. Synchronize Receipt Language dropdown with main form & update receipt UI reactively
    if (receiptLangSelect && billLangSelect) {
        receiptLangSelect.value = billLangSelect.value;
        receiptLangSelect.addEventListener('change', function () {
            billLangSelect.value = this.value;
            updateReceiptLanguage(this.value);
        });
        billLangSelect.addEventListener('change', function () {
            receiptLangSelect.value = this.value;
            updateReceiptLanguage(this.value);
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
                        syncClientAndAdDetails();
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
    if (clientNameTransInput) clientNameTransInput.addEventListener('input', syncClientAndAdDetails);
    if (customSizeInput) customSizeInput.addEventListener('input', syncClientAndAdDetails);
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
    updateReceiptLanguage(receiptLangSelect ? receiptLangSelect.value : (billLangSelect ? billLangSelect.value : 'en'));
    calculateTotal();
});
