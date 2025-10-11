/** @odoo-module **/

// Fix breadcrumb text for vehicle pages
document.addEventListener('DOMContentLoaded', function() {
    console.log('Vehicle Breadcrumb Fix: Loaded');
    
    function fixVehicleBreadcrumb() {
        try {
            // Look for breadcrumb links with title="Vehicles"
            const breadcrumbLinks = document.querySelectorAll('.o_control_panel .breadcrumb-item a[title="Vehicles"]');
            
            breadcrumbLinks.forEach(link => {
                const textElement = link.querySelector('.fw-bold.text-truncate');
                if (textElement && (!textElement.textContent || textElement.textContent.trim() === '')) {
                    console.log('Vehicle Breadcrumb Fix: Setting breadcrumb text to "Back to Vehicles"');
                    textElement.textContent = 'Back to Vehicles';
                    textElement.style.display = 'inline';
                    textElement.style.opacity = '1';
                }
            });
            
            // Also try to find any empty breadcrumb items and set them
            const emptyBreadcrumbs = document.querySelectorAll('.o_control_panel .breadcrumb-item a .fw-bold.text-truncate');
            emptyBreadcrumbs.forEach(element => {
                if (element.textContent.trim() === '' && element.closest('a').getAttribute('title') === 'Vehicles') {
                    console.log('Vehicle Breadcrumb Fix: Found empty breadcrumb, setting text');
                    element.textContent = 'Back to Vehicles';
                }
            });
            
        } catch (error) {
            console.log('Vehicle Breadcrumb Fix: Error (safe to ignore)', error);
        }
    }
    
    // Run immediately
    fixVehicleBreadcrumb();
    
    // Run every 2 seconds to catch dynamic updates
    setInterval(fixVehicleBreadcrumb, 2000);
    
    // Run when DOM changes (for SPA navigation)
    if (window.MutationObserver) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    setTimeout(fixVehicleBreadcrumb, 100);
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
});