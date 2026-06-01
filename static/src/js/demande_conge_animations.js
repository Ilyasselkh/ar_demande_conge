/** @odoo-module **/

const FORM_SELECTOR = ".o_form_view.ar_demande_conge_form";

function animateForm(form) {
    if (!form || form.dataset.arCongeAnimated === "1") {
        return;
    }
    form.dataset.arCongeAnimated = "1";

    const sheet = form.querySelector(".ar_demande_conge_sheet");
    if (sheet) {
        sheet.classList.add("ar_conge_ready");
    }

    form.querySelectorAll(".ar_request_header, .ar_request_quickfacts, .ar_request_panel").forEach((element) => {
        element.classList.add("ar_conge_reveal");
    });

    const status = form.querySelector(".ar_request_status");
    if (!status) {
        return;
    }

    let lastValue = status.textContent.trim();
    const observer = new MutationObserver(() => {
        const value = status.textContent.trim();
        if (value === lastValue) {
            return;
        }
        lastValue = value;
        status.classList.remove("ar_conge_status_flash");
        window.requestAnimationFrame(() => status.classList.add("ar_conge_status_flash"));
    });

    observer.observe(status, {
        childList: true,
        subtree: true,
        characterData: true,
    });
}

function scan() {
    document.querySelectorAll(FORM_SELECTOR).forEach(animateForm);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scan);
} else {
    scan();
}

if (document.body) {
    const bodyObserver = new MutationObserver(scan);
    bodyObserver.observe(document.body, {
        childList: true,
        subtree: true,
    });
}
