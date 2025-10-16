/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { patch } from "@web/core/utils/patch";

patch(KanbanController.prototype, {
    setup() {
        super.setup();
        this.currentStatusFilter = 'available'; // Default to available
    },

    async onMounted() {
        await super.onMounted();
        if (this.model.root.resModel === 'vehicle.vehicle') {
            // Use setTimeout to ensure DOM is fully rendered
            setTimeout(() => {
                this.setupVehicleKanbanTabs();
            }, 300); // Wait for kanban groups to render
        }
    },

    setupVehicleKanbanTabs() {
        console.log('Setting up Vehicle Kanban with group tabs');
        
        const buttons = this.rootRef.el.querySelectorAll(".o_vehicle_status_tabs .status-tab");
        const columns = this.rootRef.el.querySelectorAll(".o_kanban_group");
        
        if (!buttons.length || !columns.length) {
            console.log('No tabs or columns found, retrying...');
            setTimeout(() => this.setupVehicleKanbanTabs(), 500);
            return;
        }

        // Helper: hide all kanban columns
        const hideAllColumns = () => {
            columns.forEach(c => c.style.display = "none");
        };

        // Helper: show column matching status
        const showColumnByStatus = (status) => {
            hideAllColumns();
            
            // Map status to group title text
            const statusMap = {
                'available': 'available',
                'reserved': 'reserved',
                'maintenance': 'in maintenance'
            };
            
            const targetStatus = statusMap[status] || status;
            
            // Find matching column by title
            const group = Array.from(columns).find(c => {
                const titleEl = c.querySelector(".o_column_title, .o_kanban_header_title");
                if (!titleEl) return false;
                const title = titleEl.textContent.trim().toLowerCase();
                return title.includes(targetStatus);
            });
            
            if (group) {
                group.style.display = "block";
                console.log(`Showing group for status: ${status}`);
            } else {
                console.log(`No group found for status: ${status}`);
            }
        };

        // Setup click handlers for tabs
        buttons.forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                const status = btn.getAttribute("data-status");
                
                // Remove "active" style from all
                buttons.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                
                // Show only the selected group
                showColumnByStatus(status);
                this.currentStatusFilter = status;
            });
        });

        // Start with first group visible (available)
        hideAllColumns();
        showColumnByStatus('available');
        
        // Set first button as active
        if (buttons[0]) {
            buttons[0].classList.add("active");
        }
        
        console.log('Vehicle kanban tabs setup complete');
    }
});
