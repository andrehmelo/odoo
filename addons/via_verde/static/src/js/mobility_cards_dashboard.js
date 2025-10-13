/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

const TAB_CONFIGS = {
    via_verde: {
        label: "Via Verde",
        model: "via.verde.line",
        order: "entry_datetime desc",
        primaryFields: [
            { name: "entry_datetime", label: "Entry", type: "datetime" },
            { name: "license_plate", label: "Plate" },
            { name: "vehicle_id", label: "Vehicle", type: "many2one" },
            { name: "liquid_amount", label: "Liquid Amount", type: "monetary" },
            { name: "is_paid", label: "Paid", type: "boolean" },
            { name: "amount_due", label: "Outstanding", type: "monetary" },
        ],
        secondaryFields: [
            { name: "exit_datetime", label: "Exit", type: "datetime" },
            { name: "entry_point", label: "Entry Point" },
            { name: "exit_point", label: "Exit Point" },
            { name: "service", label: "Service" },
            { name: "service_description", label: "Service Description" },
            { name: "market", label: "Market" },
            { name: "market_description", label: "Market Description" },
            { name: "amount", label: "Gross", type: "monetary" },
            { name: "discount_amount", label: "Discount", type: "monetary" },
            { name: "discount_percentage", label: "Discount %" },
            { name: "discount_balance", label: "Discount Balance", type: "monetary" },
            { name: "payment_date", label: "Payment Date", type: "date" },
            { name: "payment_method", label: "Payment Method" },
            { name: "contract_number", label: "Contract" },
            { name: "mobility_account", label: "Mobility Account" },
            { name: "iai", label: "IAI" },
            { name: "obu", label: "OBU" },
            { name: "notes", label: "Notes" },
        ],
        extraFields: ["currency_id"],
        newContext: {},
    },
    gas_card: {
        label: "Cartões Combustível",
        model: "gas.card.line",
        order: "transaction_datetime desc",
        primaryFields: [
            { name: "transaction_date", label: "Date", type: "date" },
            { name: "transaction_time", label: "Time" },
            { name: "card_number", label: "Card" },
            { name: "card_description", label: "Label" },
            { name: "client_name", label: "Client" },
            { name: "vehicle_id", label: "Vehicle", type: "many2one" },
            { name: "driver_id", label: "Driver", type: "many2one" },
            { name: "fuel_type", label: "Fuel" },
            { name: "liters", label: "Liters" },
            { name: "net_amount", label: "Net", type: "monetary" },
            { name: "total_amount", label: "Total", type: "monetary" },
            { name: "kilometers", label: "KM" },
            { name: "is_paid", label: "Paid", type: "boolean" },
            { name: "amount_due", label: "Outstanding", type: "monetary" },
        ],
        secondaryFields: [
            { name: "station_name", label: "Station" },
            { name: "network_type", label: "Network" },
            { name: "unit_of_measure", label: "Unit" },
            { name: "unit_price_excl_vat", label: "Unit Price (excl. VAT)", type: "monetary" },
            { name: "vat_amount", label: "VAT", type: "monetary" },
            { name: "reference_amount", label: "Reference (incl. VAT)", type: "monetary" },
            { name: "discount_amount", label: "Discount", type: "monetary" },
            { name: "receipt_number", label: "Receipt" },
            { name: "invoice_number", label: "Invoice" },
            { name: "payment_date", label: "Payment Date", type: "date" },
            { name: "driver_identifier", label: "Driver Ref." },
            { name: "notes", label: "Notes" },
        ],
        extraFields: ["currency_id"],
        newContext: {},
    },
};

export class MobilityCardsDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.dialogService = useService("dialog");
        this.state = useState({
            activeTab: "via_verde",
            loading: true,
            rows: [],
            expanded: {},
        });
        onWillStart(() => this._loadData());
    }

    get tabList() {
        return Object.entries(TAB_CONFIGS).map(([key, config]) => ({
            key,
            label: config.label,
        }));
    }

    get activeConfig() {
        return TAB_CONFIGS[this.state.activeTab];
    }

    async _loadData() {
        this.state.loading = true;
        const config = this.activeConfig;
        const fields = [
            ...config.primaryFields.map((f) => f.name),
            ...config.secondaryFields.map((f) => f.name),
            "currency_id",
        ];
        if (config.extraFields) {
            for (const field of config.extraFields) {
                if (!fields.includes(field)) {
                    fields.push(field);
                }
            }
        }
        const rows = await this.orm.searchRead(config.model, [], fields, {
            order: config.order,
            limit: 100,
        });
        this.state.rows = rows;
        this.state.expanded = {};
        this.state.loading = false;
    }

    async switchTab(key) {
        if (this.state.activeTab === key) {
            return;
        }
        this.state.activeTab = key;
        await this._loadData();
    }

    toggleRow(rowId) {
        this.state.expanded[rowId] = !this.state.expanded[rowId];
    }

    formatField(field, row) {
        const value = row[field.name];
        if (value === false || value === null || value === undefined || value === "") {
            return "-";
        }
        switch (field.type) {
            case "monetary":
                return this.env.services.localization.monetary(value, this._currencyFromRow(row));
            case "boolean":
                return value ? _t("Yes") : _t("No");
            case "datetime":
                return this.env.services.localization.formatDatetime(value);
            case "date":
                return this.env.services.localization.formatDate(value);
            case "many2one":
                return Array.isArray(value) ? value[1] : value;
            default:
                return value;
        }
    }

    _currencyFromRow(row) {
        if (!row || !row.currency_id) {
            const userCurrency = this.env.services.user && this.env.services.user.currency;
            return userCurrency ? userCurrency.id : false;
        }
        return Array.isArray(row.currency_id) ? row.currency_id[0] : row.currency_id;
    }

    onToggleDetails(row) {
        this.toggleRow(row.id);
    }

    async onNewRecord() {
        const config = this.activeConfig;
        this.dialogService.add(FormViewDialog, {
            resModel: config.model,
            context: config.newContext,
            onRecordSaved: () => this._loadData(),
        });
    }

    async onImport() {
        const config = this.activeConfig;
        // TODO: Replace drag-and-drop upload with direct provider import once APIs are available.
        await this.actionService.doAction({
            type: "ir.actions.client",
            tag: "import",
            params: { model: config.model },
        });
        await this._loadData();
    }
}

MobilityCardsDashboard.template = "via_verde.MobilityCardsDashboard";

registry.category("actions").add("via_verde_mobility_cards_dashboard", MobilityCardsDashboard);
