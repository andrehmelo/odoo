/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { useService } from "@web/core/utils/hooks";

export class CheckInKanbanController extends KanbanController {
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

export const checkInKanbanView = {
    ...kanbanView,
    Controller: CheckInKanbanController,
    buttonTemplate: "vehicle_checkin.KanbanController.Buttons",
};

registry.category("views").add("checkin_kanban", checkInKanbanView);
