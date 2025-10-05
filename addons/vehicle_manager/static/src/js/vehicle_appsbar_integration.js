/** @odoo-module **/

import { registry } from '@web/core/registry';
import { FormController } from '@web/views/form/form_controller';
import { patch } from '@web/core/utils/patch';

// Patch to handle appsbar layout adjustments for vehicle forms
patch(FormController.prototype, 'vehicle_appsbar_integration', {
    setup() {
        super.setup();
        
        // Add layout adjustment when the component is mounted
        this.onMounted(() => {
            this._adjustLayoutForAppsbar();
        });
    },

    _adjustLayoutForAppsbar() {
        if (this.props.resModel === 'vehicle.vehicle') {
            const webClient = document.querySelector('.o_web_client');
            const appsbarPanel = document.querySelector('.mk_apps_sidebar_panel');
            const actionManager = document.querySelector('.o_action_manager');
            
            if (webClient && appsbarPanel && actionManager) {
                // Add a class to identify when appsbar is present
                webClient.classList.add('mk-appsbar-layout');
                
                // Ensure proper content spacing
                const formView = actionManager.querySelector('.o_form_view');
                if (formView) {
                    formView.classList.add('mk-appsbar-adjusted');
                }
            }
        }
    }
});