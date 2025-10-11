/** @odoo-module **/

import { FormController } from '@web/views/form/form_controller';
import { patch } from '@web/core/utils/patch';

patch(FormController.prototype, 'vehicle_form_controller', {
    
    setup() {
        this._super(...arguments);
        this._updateButtonText();
    },
    
    /**
     * Override to update button text based on form mode
     */
    _updateButtonText() {
        if (this.model.config.resModel === 'vehicle.vehicle') {
            const createButton = document.querySelector('.o_control_panel_main_buttons .o_form_button_create');
            const saveButton = document.querySelector('.o_control_panel_main_buttons .o_form_button_save');
            const editButton = document.querySelector('.o_control_panel_main_buttons .o_form_button_edit');
            
            // Update button text based on mode
            setTimeout(() => {
                if (this.model.root.isInEdition) {
                    // In edit mode - show Save
                    if (createButton) createButton.textContent = 'Save';
                    if (saveButton) saveButton.textContent = 'Save';
                } else {
                    // In view mode - show New
                    if (createButton) createButton.textContent = 'New';
                    if (editButton) editButton.textContent = 'Edit';
                }
            }, 100);
        }
    },
    
    /**
     * Override mode changes to update button text
     */
    async switchMode(mode) {
        const result = await this._super(...arguments);
        this._updateButtonText();
        return result;
    },
    
    /**
     * Override save action to update button text
     */
    async save() {
        const result = await this._super(...arguments);
        this._updateButtonText();
        return result;
    }
});