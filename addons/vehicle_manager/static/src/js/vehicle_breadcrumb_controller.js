/** @odoo-module **/

// Enhanced breadcrumb modification for vehicle forms
document.addEventListener('DOMContentLoaded', function() {
    console.log('Vehicle Manager: Enhanced breadcrumb controller loaded');
    
    function updateVehicleBreadcrumb() {
        try {
            // Check if we're in a vehicle form page
            const isVehicleForm = window.location.href.includes('vehicle.vehicle') && 
                                  document.querySelector('.o_form_view');
            
            if (isVehicleForm) {
                // Find ALL possible breadcrumb selectors
                const selectors = [
                    '.o_control_panel .breadcrumb .breadcrumb-item a',
                    '.o_control_panel .breadcrumb a',
                    '.breadcrumb .breadcrumb-item a',
                    '.breadcrumb a'
                ];
                
                let found = false;
                selectors.forEach(selector => {
                    const links = document.querySelectorAll(selector);
                    links.forEach(link => {
                        const text = link.textContent.trim();
                        if ((text === 'Vehicles' || text.includes('Vehicle')) && !text.includes('Go back to')) {
                            link.innerHTML = '<i class="fa fa-arrow-left me-2"></i>Go back to vehicles';
                            link.style.fontWeight = '500';
                            link.style.color = '#007bff';
                            link.style.textDecoration = 'none';
                            link.style.display = 'inline-flex';
                            link.style.alignItems = 'center';
                            link.style.gap = '8px';
                            link.style.marginLeft = '20px';
                            link.style.transition = 'all 0.2s ease';
                            found = true;
                            
                            // Add hover effect
                            link.addEventListener('mouseenter', function() {
                                this.style.color = '#0056b3';
                                this.style.transform = 'translateX(-2px)';
                            });
                            
                            link.addEventListener('mouseleave', function() {
                                this.style.color = '#007bff';
                                this.style.transform = 'translateX(0)';
                            });
                        }
                    });
                });
                
                if (found) {
                    console.log('Vehicle Manager: Breadcrumb updated to "Go back to vehicles"');
                }
            }
        } catch (error) {
            // Silently handle any errors to prevent breaking the UI
            console.log('Vehicle Manager: Breadcrumb update skipped', error);
        }
    }
    
    // Run immediately and more frequently to catch dynamic changes
    updateVehicleBreadcrumb();
    setInterval(updateVehicleBreadcrumb, 500); // More frequent checks
    
    // Also run when the URL changes (for SPA navigation)
    let lastUrl = location.href;
    new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            setTimeout(updateVehicleBreadcrumb, 50);
            setTimeout(updateVehicleBreadcrumb, 200);
            setTimeout(updateVehicleBreadcrumb, 500);
        }
    }).observe(document, {subtree: true, childList: true});
    
    // Additional observer specifically for breadcrumb changes
    const breadcrumbObserver = new MutationObserver(() => {
        setTimeout(updateVehicleBreadcrumb, 100);
    });
    
    // Start observing breadcrumb changes
    setTimeout(() => {
        const breadcrumbContainer = document.querySelector('.o_control_panel .breadcrumb');
        if (breadcrumbContainer) {
            breadcrumbObserver.observe(breadcrumbContainer, {
                childList: true,
                subtree: true,
                characterData: true
            });
        }
    }, 1000);
});