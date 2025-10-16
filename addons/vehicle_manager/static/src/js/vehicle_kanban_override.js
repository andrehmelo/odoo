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
                this.setupVehicleKanban();
            }, 0);
        }
    },

    setupVehicleKanban() {
        console.log('Setting up Vehicle Kanban with tabs');
        
        // Setup status tab navigation only
        this.setupStatusTabs();
        
        // Filter cards initially (show available)
        this.filterCardsByStatus('available');
        
        // Update status counts
        this.updateStatusCounts();
    },

    setupStatusTabs() {
        const tabs = this.rootRef.el.querySelectorAll('.status-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const status = tab.dataset.status;
                
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Filter cards
                this.filterCardsByStatus(status);
                this.currentStatusFilter = status;
            });
        });
        
        // Set initial active tab
        const availableTab = this.rootRef.el.querySelector('.status-tab[data-status="available"]');
        if (availableTab) {
            availableTab.classList.add('active');
        }
    },

    filterCardsByStatus(status) {
        const allCards = this.rootRef.el.querySelectorAll('.o_vehicle_card');
        allCards.forEach(card => {
            if (card.dataset.status === status) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    },

    updateStatusCounts() {
        const allCards = this.rootRef.el.querySelectorAll('.o_vehicle_card');
        const counts = { available: 0, reserved: 0, maintenance: 0 };
        
        allCards.forEach(card => {
            const status = card.dataset.status;
            if (counts.hasOwnProperty(status)) {
                counts[status]++;
            }
        });
        
        // Update badge counts
        Object.keys(counts).forEach(status => {
            const badge = this.rootRef.el.querySelector(`.status-tab[data-status="${status}"] .badge`);
            if (badge) {
                badge.textContent = counts[status];
            }
        });
    }
});
