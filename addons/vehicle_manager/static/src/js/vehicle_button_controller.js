/** @odoo-module **/

// Enhanced button controller for vehicle forms
document.addEventListener('DOMContentLoaded', function() {
    console.log('Vehicle Manager: Enhanced button controller loaded');
    
    let lastButtonText = '';
    let lastFormState = '';
    
    // Function to update vehicle form buttons
    function updateVehicleButtons() {
        try {
            // Only run on vehicle pages
            const currentUrl = window.location.href;
            if (!currentUrl.includes('vehicle.vehicle')) {
                return;
            }
            
            // Find the New/Create button in control panel
            const newButton = document.querySelector('.o_cp_buttons .o_list_button_add, .o_cp_buttons .o_form_button_create, .o_cp_buttons .btn[data-hotkey="c"]');
            
            if (!newButton) {
                return;
            }
            
            // Detect current view state
            const isKanbanView = document.querySelector('.o_kanban_view');
            const isListView = document.querySelector('.o_list_view');
            const isFormView = document.querySelector('.o_form_view');
            const isFormEditable = document.querySelector('.o_form_editable, .o_form_view.o_form_editable');
            const isNewRecord = currentUrl.includes('action') && currentUrl.includes('view_type=form') && !currentUrl.match(/\/\d+/);
            
            let currentState = '';
            let newButtonText = '';
            
            if (isKanbanView || isListView) {
                // In kanban or list view - show "New"
                currentState = 'list';
                newButtonText = 'New';
            } else if (isFormView && (isFormEditable || isNewRecord)) {
                // In form view and editing or creating - show "Save"
                currentState = 'editing';
                newButtonText = 'Save';
            } else if (isFormView) {
                // In form view but not editing - show "New" 
                currentState = 'viewing';
                newButtonText = 'New';
            }
            
            // Only update if state or button text changed
            const currentButtonText = newButton.textContent.trim();
            if (currentState !== lastFormState || (newButtonText && currentButtonText !== newButtonText)) {
                if (newButtonText && currentButtonText !== newButtonText) {
                    newButton.textContent = newButtonText;
                    console.log(`Vehicle Manager: Button changed from "${currentButtonText}" to "${newButtonText}" (state: ${currentState})`);
                }
                lastFormState = currentState;
                lastButtonText = newButtonText;
            }
            
        } catch (error) {
            // Silently handle any errors to prevent breaking the UI
            console.log('Vehicle Manager: Button update error:', error.message);
        }
    }
    
    // Run periodically to catch state changes
    setInterval(updateVehicleButtons, 500);
    
    // Also run on URL changes (for SPA navigation)
    let currentUrl = window.location.href;
    setInterval(function() {
        if (window.location.href !== currentUrl) {
            currentUrl = window.location.href;
            setTimeout(updateVehicleButtons, 100); // Small delay for DOM to update
        }
    }, 200);
    
    // Run immediately
    setTimeout(updateVehicleButtons, 100);
});