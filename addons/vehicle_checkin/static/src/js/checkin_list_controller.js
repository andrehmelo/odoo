/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";

export class CheckInListController extends ListController {
    setup() {
        super.setup();
        this.action = useService("action");
    }

    async onClickNewCheckIn() {
        await this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'New Check-In',
            res_model: 'vehicle.checkin.wizard',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new',
        });
        // Reload the view after wizard closes
        await this.model.root.load();
        this.render();
    }
}

export const checkInListView = {
    ...listView,
    Controller: CheckInListController,
    buttonTemplate: "vehicle_checkin.ListController.Buttons",
};

registry.category("views").add("checkin_list", checkInListView);
