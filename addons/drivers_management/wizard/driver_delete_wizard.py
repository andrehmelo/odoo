# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DriverDeleteWizard(models.TransientModel):
    _name = 'driver.delete.wizard'
    _description = 'Driver Delete Wizard'

    delete_type = fields.Selection([
        ('all_drivers', 'Delete All Drivers'),
        ('leads_only', 'Delete Only Leads'),
        ('inactive_only', 'Delete Only Inactive'),
    ], string='Delete Option', required=True, default='all_drivers')
    
    confirm_delete = fields.Boolean(
        string='I confirm this action',
        help="Check this box to confirm the deletion"
    )
    
    item_count = fields.Char(
        string='Items to Process',
        compute='_compute_item_count'
    )
    
    warning_message = fields.Char(
        string='Warning',
        compute='_compute_item_count'
    )

    @api.depends('delete_type')
    def _compute_item_count(self):
        """Calculate what will be affected by the action"""
        Driver = self.env['drivers.management']
        
        for wizard in self:
            wizard.warning_message = False
            
            if wizard.delete_type == 'all_drivers':
                total_count = Driver.search_count([])
                lead_count = Driver.search_count([('status', '=', 'lead')])
                inactive_count = Driver.search_count([('status', '=', 'inactive')])
                active_count = Driver.search_count([('status', '=', 'active')])
                
                wizard.item_count = f"{total_count} driver(s) ({lead_count} leads, {inactive_count} inactive, {active_count} active)"
                if active_count > 0:
                    wizard.warning_message = f"⚠️ {active_count} active driver(s) will be released from their vehicles!"
                
            elif wizard.delete_type == 'leads_only':
                lead_count = Driver.search_count([('status', '=', 'lead')])
                wizard.item_count = f"{lead_count} lead(s)"
                
            elif wizard.delete_type == 'inactive_only':
                inactive_count = Driver.search_count([('status', '=', 'inactive')])
                wizard.item_count = f"{inactive_count} inactive driver(s)"
            
            else:
                wizard.item_count = "0 items"

    def _cleanup_driver_checkins(self, driver):
        """Clean up all check-ins for a driver being deleted"""
        Checkin = self.env['vehicle.checkin']
        
        # Find ALL check-ins for this driver
        all_checkins = Checkin.search([('driver_id', '=', driver.id)])
        
        for checkin in all_checkins:
            # For active check-ins, release the vehicle first
            if checkin.state == 'checked_in' and checkin.vehicle_id:
                checkin.vehicle_id.write({'status': 'available'})
        
        # Delete all check-in records for this driver (force delete to bypass protection)
        all_checkins.with_context(force_delete=True).unlink()
        
        # Also clear vehicle_id on driver (in case it's set directly)
        if driver.vehicle_id:
            driver.vehicle_id.write({'status': 'available'})

    def action_delete_drivers(self):
        """Process deletion based on selected criteria"""
        if not self.confirm_delete:
            raise UserError(_("Please confirm the action by checking the confirmation box."))
        
        Driver = self.env['drivers.management']
        message = ""
        
        if self.delete_type == 'all_drivers':
            drivers = Driver.search([])
            
            if not drivers:
                raise UserError(_("No drivers found."))
            
            driver_count = len(drivers)
            active_count = len(drivers.filtered(lambda d: d.status == 'active'))
            
            # Clean up ALL drivers' check-ins before deletion
            for driver in drivers:
                self._cleanup_driver_checkins(driver)
            
            # Now delete all - use context to skip platform validation
            drivers.with_context(skip_platform_validation=True).write({'status': 'inactive', 'vehicle_id': False})
            drivers.unlink()
            
            if active_count > 0:
                message = _('%d driver(s) deleted. %d active driver(s) were released from their vehicles.') % (driver_count, active_count)
            else:
                message = _('%d driver(s) have been deleted.') % driver_count
            
        elif self.delete_type == 'leads_only':
            leads = Driver.search([('status', '=', 'lead')])
            
            if not leads:
                raise UserError(_("No leads found."))
            
            lead_count = len(leads)
            leads.unlink()
            message = _('%d lead(s) have been deleted.') % lead_count
            
        elif self.delete_type == 'inactive_only':
            inactive = Driver.search([('status', '=', 'inactive')])
            
            if not inactive:
                raise UserError(_("No inactive drivers found."))
            
            inactive_count = len(inactive)
            
            # Clean up check-in history for inactive drivers
            for driver in inactive:
                self._cleanup_driver_checkins(driver)
            
            inactive.unlink()
            message = _('%d inactive driver(s) have been deleted.') % inactive_count
        
        # Show notification and reload the page
        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
            'type': 'success',
            'title': _('Deletion Complete'),
            'message': message,
            'sticky': False,
        })
        
        # Return reload action to force refresh the current view
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
