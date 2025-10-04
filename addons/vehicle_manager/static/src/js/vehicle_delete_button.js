/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

// Patch List Controller to add Delete Vehicles button
patch(ListController.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
    },

    get actionMenuItems() {
        const items = super.actionMenuItems || {};
        if (this.props.resModel === "vehicle.vehicle") {
            return {
                ...items,
                action: [
                    ...(items.action || []),
                    {
                        description: "Delete Vehicles",
                        callback: () => this.openDeleteWizard(),
                    },
                ],
            };
        }
        return items;
    },

    async openDeleteWizard() {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Delete Vehicles",
            res_model: "vehicle.delete.wizard",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: {},
        });
    },
});

// Patch Kanban Controller to add Delete Vehicles button
patch(KanbanController.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
    },

    get actionMenuItems() {
        const items = super.actionMenuItems || {};
        if (this.props.resModel === "vehicle.vehicle") {
            return {
                ...items,
                action: [
                    ...(items.action || []),
                    {
                        description: "Delete Vehicles",
                        callback: () => this.openDeleteWizard(),
                    },
                ],
            };
        }
        return items;
    },

    async openDeleteWizard() {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Delete Vehicles",
            res_model: "vehicle.delete.wizard",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: {},
        });
    },
});