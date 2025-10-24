/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class CheckInDashboard extends Component {
    setup() {
        this.action = useService("action");
    }

    openCheckInWizard() {
        this.action.doAction("vehicle_checkin.action_vehicle_checkin_wizard");
    }

    openCheckOutWizard() {
        this.action.doAction("vehicle_checkin.action_direct_checkout_wizard");
    }

    openAllCheckIns() {
        this.action.doAction("vehicle_checkin.action_vehicle_checkin");
    }

    openActiveWithFilter() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "vehicle.checkin",
            views: [[false, "list"], [false, "form"]],
            context: { search_default_filter_checked_in: 1 },
        });
    }

    openCompletedWithFilter() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "vehicle.checkin",
            views: [[false, "list"], [false, "form"]],
            context: { search_default_filter_checked_out: 1 },
        });
    }
}

CheckInDashboard.template = "vehicle_checkin.Dashboard";

registry.category("actions").add("vehicle_checkin_dashboard", CheckInDashboard);
