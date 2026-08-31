/** @odoo-module **/

import { onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";

const MODEL = "ar.demande.conge";
const FILTER_ACCESS_GROUP = "ar_demande_conge.group_demande_conge_validateur_rh";
const FILTER_CLASS = "ar_conge_custom_filters";
const STORAGE_KEY = "ar_demande_conge_filters";
const DEMANDE_TYPES = [
    ["", "Tous"],
    ["conge", "Demande de congé"],
    ["teletravail", "Demande de télétravail"],
    ["recuperation", "Demande d'ajout de récupération"],
    ["heures_supp", "Demande des heures supplémentaires"],
];

function removeCongeFilters() {
    document.querySelectorAll(`.${FILTER_CLASS}`).forEach((panel) => panel.remove());
}

function formatDate(date) {
    return date.toISOString().slice(0, 10);
}

function savedState() {
    try {
        return JSON.parse(window.sessionStorage.getItem(STORAGE_KEY) || "{}");
    } catch {
        return {};
    }
}

function saveState(state) {
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function pageKind() {
    const title = document.querySelector(".o_control_panel")?.textContent || "";
    if (title.includes("Demandes acceptées")) {
        return "accepted";
    }
    if (title.includes("Demandes refusées")) {
        return "refused";
    }
    return "main";
}

function baseDomain(kind) {
    if (kind === "accepted") {
        return [["state", "=", "acceptee"]];
    }
    if (kind === "refused") {
        return [["state", "=", "refusee"]];
    }
    return [["state", "not in", ["acceptee", "refusee"]]];
}

function periodDomain(period, dateFrom, dateTo) {
    const today = new Date();
    let start = null;
    let end = null;

    if (period === "this_week") {
        start = new Date(today);
        start.setDate(today.getDate() - 7);
    } else if (period === "this_month") {
        start = new Date(today);
        start.setDate(today.getDate() - 30);
    } else if (period === "this_year") {
        start = new Date(today);
        start.setDate(today.getDate() - 360);
    } else if (period === "custom" && dateFrom && dateTo) {
        start = new Date(`${dateFrom}T00:00:00`);
        end = new Date(`${dateTo}T00:00:00`);
        if (start > end) {
            [start, end] = [end, start];
        }
    }

    if (!start) {
        return [];
    }

    const domain = [["date_debut", ">=", formatDate(start)]];
    if (end) {
        end.setDate(end.getDate() + 1);
        domain.push(["date_debut", "<", formatDate(end)]);
    }
    return domain;
}

function option(value, label, selected) {
    const element = document.createElement("option");
    element.value = value;
    element.textContent = label;
    element.selected = String(value) === String(selected || "");
    return element;
}

async function employees(orm) {
    try {
        return await orm.searchRead("hr.employee", [], ["name"], { order: "name" });
    } catch {
        return [];
    }
}

async function canShowFilters() {
    try {
        return await user.hasGroup(FILTER_ACCESS_GROUP);
    } catch {
        return false;
    }
}

function makePanel(employeeList) {
    const state = savedState();
    const selectedEmployee = employeeList.find((employee) => String(employee.id) === String(state.personId || ""));
    const panel = document.createElement("div");
    panel.className = FILTER_CLASS;
    panel.innerHTML = `
        <div class="ar_conge_filter_header">
            <span class="ar_conge_filter_dot"></span>
            <span>Filtres personnalisés</span>
        </div>
        <div class="ar_conge_filter_grid">
            <label class="ar_conge_filter_field" for="ar_conge_filter_period">
                <span>Période</span>
                <select id="ar_conge_filter_period" class="ar_conge_filter_control">
                    <option value="">Toutes les périodes</option>
                    <option value="this_year">Cette année</option>
                    <option value="this_month">Ce mois</option>
                    <option value="this_week">Cette semaine</option>
                    <option value="custom">Période</option>
                </select>
            </label>
            <label class="ar_conge_filter_field" for="ar_conge_filter_person">
                <span>Personne</span>
                <input id="ar_conge_filter_person"
                       class="ar_conge_filter_control"
                       type="text"
                       list="ar_conge_filter_people"
                       placeholder="Écrire un nom..."
                       autocomplete="off"/>
                <datalist id="ar_conge_filter_people"></datalist>
            </label>
            <label class="ar_conge_filter_field" for="ar_conge_filter_type">
                <span>Type de demande</span>
                <select id="ar_conge_filter_type" class="ar_conge_filter_control"></select>
            </label>
        </div>
        <div class="ar_conge_filter_dates">
            <label class="ar_conge_filter_date" for="ar_conge_filter_from">
                <span>De</span>
                <input id="ar_conge_filter_from" class="ar_conge_filter_control" type="date"/>
            </label>
            <label class="ar_conge_filter_date" for="ar_conge_filter_to">
                <span>À</span>
                <input id="ar_conge_filter_to" class="ar_conge_filter_control" type="date"/>
            </label>
            <button type="button" class="ar_conge_filter_apply">Appliquer</button>
            <button type="button" class="ar_conge_filter_reset">Réinitialiser</button>
        </div>
    `;

    const period = panel.querySelector("#ar_conge_filter_period");
    const person = panel.querySelector("#ar_conge_filter_person");
    const people = panel.querySelector("#ar_conge_filter_people");
    const type = panel.querySelector("#ar_conge_filter_type");
    const dateFrom = panel.querySelector("#ar_conge_filter_from");
    const dateTo = panel.querySelector("#ar_conge_filter_to");

    period.value = state.period || "";
    for (const employee of employeeList) {
        people.appendChild(option(employee.name, employee.name, state.personQuery));
    }
    for (const [value, label] of DEMANDE_TYPES) {
        type.appendChild(option(value, label, state.demandeType));
    }
    person.value = state.personQuery || selectedEmployee?.name || "";
    dateFrom.value = state.dateFrom || "";
    dateTo.value = state.dateTo || "";

    return panel;
}

function bindPanel(panel, action, employeeList) {
    const period = panel.querySelector("#ar_conge_filter_period");
    const person = panel.querySelector("#ar_conge_filter_person");
    const type = panel.querySelector("#ar_conge_filter_type");
    const dateFrom = panel.querySelector("#ar_conge_filter_from");
    const dateTo = panel.querySelector("#ar_conge_filter_to");
    const apply = panel.querySelector(".ar_conge_filter_apply");
    const reset = panel.querySelector(".ar_conge_filter_reset");
    const dates = panel.querySelector(".ar_conge_filter_dates");

    const matchedEmployee = () => {
        const query = person.value.trim().toLowerCase();
        return employeeList.find((employee) => employee.name.toLowerCase() === query);
    };

    const refreshDates = () => {
        dates.classList.toggle("d-none", period.value !== "custom");
        apply.disabled = period.value === "custom" && (!dateFrom.value || !dateTo.value);
    };

    const applyFilters = () => {
        const kind = pageKind();
        const employee = matchedEmployee();
        const personQuery = person.value.trim();
        const state = {
            period: period.value,
            personId: employee?.id || "",
            personQuery,
            demandeType: type.value,
            dateFrom: dateFrom.value,
            dateTo: dateTo.value,
        };
        saveState(state);

        const domain = [...baseDomain(kind), ...periodDomain(state.period, state.dateFrom, state.dateTo)];
        if (employee) {
            domain.push(["demandeur_id", "=", Number(state.personId)]);
        } else if (personQuery) {
            domain.push(["demandeur_id", "ilike", personQuery]);
        }
        if (state.demandeType) {
            domain.push(["demande_type", "=", state.demandeType]);
        }

        action.doAction({
            type: "ir.actions.act_window",
            name: kind === "accepted" ? "Demandes acceptées" : kind === "refused" ? "Demandes refusées" : "Demandes",
            res_model: MODEL,
            views: [[false, "list"], [false, "kanban"], [false, "form"]],
            domain,
            target: "current",
        });
    };

    period.addEventListener("change", () => {
        refreshDates();
        if (period.value !== "custom") {
            applyFilters();
        }
    });
    person.addEventListener("change", applyFilters);
    person.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
            ev.preventDefault();
            applyFilters();
        }
    });
    type.addEventListener("change", applyFilters);
    dateFrom.addEventListener("change", refreshDates);
    dateTo.addEventListener("change", refreshDates);
    apply.addEventListener("click", applyFilters);
    reset.addEventListener("click", () => {
        period.value = "";
        person.value = "";
        type.value = "";
        dateFrom.value = "";
        dateTo.value = "";
        refreshDates();
        applyFilters();
    });
    refreshDates();
}

export class DemandeCongeListController extends ListController {
    setup() {
        super.setup();
        this.action = useService("action");
        this.orm = useService("orm");
        this.congeFilterPanel = null;
        this.congeFilterTimeouts = [];
        this.congeFilterUnmounted = false;
        onMounted(() => this.addCongeFilters());
        onWillUnmount(() => {
            this.congeFilterUnmounted = true;
            this.congeFilterTimeouts.forEach((timeoutId) => window.clearTimeout(timeoutId));
            this.congeFilterTimeouts = [];
            this.congeFilterPanel?.remove();
            this.congeFilterPanel = null;
            removeCongeFilters();
        });
    }

    retryAddCongeFilters(attempt) {
        const timeoutId = window.setTimeout(() => {
            this.congeFilterTimeouts = this.congeFilterTimeouts.filter((id) => id !== timeoutId);
            if (!this.congeFilterUnmounted) {
                this.addCongeFilters(attempt + 1);
            }
        }, 100);
        this.congeFilterTimeouts.push(timeoutId);
    }

    async addCongeFilters(attempt = 0) {
        if (this.congeFilterUnmounted) {
            return;
        }
        const resModel = this.props?.resModel || this.model?.root?.resModel;
        if (resModel && resModel !== MODEL) {
            removeCongeFilters();
            return;
        }
        if (!(await canShowFilters())) {
            removeCongeFilters();
            return;
        }
        const content =
            document.querySelector(".o_action_manager .o_action:not(.o_inactive_modifier) .o_content") ||
            document.querySelector(".o_action_manager .o_content");
        const list =
            content?.querySelector(".o_list_renderer")?.closest(".o_list_view") ||
            content?.querySelector(".o_list_view") ||
            content?.querySelector(".o_list_table")?.closest(".o_list_view") ||
            content?.firstElementChild;

        const host = list?.parentElement;
        if ((!content || !list || !host) && attempt < 30) {
            this.retryAddCongeFilters(attempt);
            return;
        }
        if (!content || !list || !host || content.querySelector(`.${FILTER_CLASS}`)) {
            return;
        }

        const employeeList = await employees(this.orm);
        const panel = makePanel(employeeList);
        if (this.congeFilterUnmounted || list.parentElement !== host) {
            if (!this.congeFilterUnmounted && attempt < 30) {
                this.retryAddCongeFilters(attempt);
            }
            return;
        }
        panel.dataset.resModel = MODEL;
        bindPanel(panel, this.action, employeeList);
        if (list.parentElement !== host) {
            if (attempt < 30) {
                this.retryAddCongeFilters(attempt);
            }
            return;
        }
        host.insertBefore(panel, list);
        this.congeFilterPanel = panel;
    }
}

registry.category("views").add("ar_demande_conge_list", {
    ...listView,
    Controller: DemandeCongeListController,
});
