# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VehicleDeleteWizard(models.TransientModel):
    _name = 'vehicle.delete.wizard'
    _description = 'Vehicle Delete Wizard'

    delete_type = fields.Selection([
        ('all_vehicles', 'Delete All Vehicles'),
        ('current_interventions', 'Remove Current Interventions'),
        ('completed_maintenances', 'Remove Completed Maintenances'),
        ('all_maintenances', 'Remove All Maintenances'),
    ], string='Delete Option', required=True, default='all_vehicles')
    
    confirm_delete = fields.Boolean(
        string='I confirm this action',
        help="Check this box to confirm the deletion"
    )
    
    item_count = fields.Char(
        string='Items to Process',
        compute='_compute_item_count'
    )

    @api.depends('delete_type')
    def _compute_item_count(self):
        """Calculate what will be affected by the action"""
        for wizard in self:
            Vehicle = self.env['vehicle.vehicle']
            Intervention = self.env['car.intervention.history']
            
            if wizard.delete_type == 'all_vehicles':
                vehicle_count = Vehicle.search_count([])
                maintenance_count = Intervention.search_count([])
                wizard.item_count = f"{vehicle_count} vehicle(s) and {maintenance_count} maintenance record(s)"
                
            elif wizard.delete_type == 'current_interventions':
                current_count = Intervention.search_count([('state', '=', 'in_maintenance')])
                wizard.item_count = f"{current_count} active intervention(s)"
                
            elif wizard.delete_type == 'completed_maintenances':
                completed_count = Intervention.search_count([('state', '=', 'completed')])
                wizard.item_count = f"{completed_count} completed maintenance record(s)"
                
            elif wizard.delete_type == 'all_maintenances':
                maintenance_count = Intervention.search_count([])
                wizard.item_count = f"{maintenance_count} maintenance record(s)"
            
            else:
                wizard.item_count = "0 items"

    def action_delete_vehicles(self):
        """Process deletion based on selected criteria"""
        if not self.confirm_delete:
            raise UserError(_("Please confirm the action by checking the confirmation box."))
        
        Vehicle = self.env['vehicle.vehicle']
        Intervention = self.env['car.intervention.history']
        
        message = ""
        
        if self.delete_type == 'all_vehicles':
            # Delete all vehicles (which cascades to all interventions)
            vehicles = Vehicle.search([])
            vehicle_count = len(vehicles)
            maintenance_count = Intervention.search_count([])
            
            if not vehicles:
                raise UserError(_("No vehicles found."))
            
            vehicles.unlink()
            message = _('%d vehicle(s) and %d maintenance record(s) have been deleted.') % (vehicle_count, maintenance_count)
            
        elif self.delete_type == 'current_interventions':
            # Remove current interventions - vehicles go back to available
            current_interventions = Intervention.search([('state', '=', 'in_maintenance')])
            
            if not current_interventions:
                raise UserError(_("No active interventions found."))
            
            count = len(current_interventions)
            
            # Set all vehicles in maintenance back to available
            for intervention in current_interventions:
                if intervention.vehicle_id and intervention.vehicle_id.status == 'maintenance':
                    intervention.vehicle_id.write({'status': 'available'})
            
            # Delete the interventions
            current_interventions.unlink()
            message = _('%d active intervention(s) removed. Vehicles set to available.') % count
            
        elif self.delete_type == 'completed_maintenances':
            # Delete only completed maintenance records
            completed_maintenances = Intervention.search([('state', '=', 'completed')])
            
            if not completed_maintenances:
                raise UserError(_("No completed maintenance records found."))
            
            count = len(completed_maintenances)
            completed_maintenances.unlink()
            message = _('%d completed maintenance record(s) have been deleted.') % count
            
        elif self.delete_type == 'all_maintenances':
            # Remove all maintenance records (current and completed)
            all_interventions = Intervention.search([])
            
            if not all_interventions:
                raise UserError(_("No maintenance records found."))
            
            count = len(all_interventions)
            
            # Set all vehicles in maintenance back to available
            vehicles_in_maintenance = Vehicle.search([('status', '=', 'maintenance')])
            vehicles_in_maintenance.write({'status': 'available'})
            
            # Delete all interventions
            all_interventions.unlink()
            message = _('%d maintenance record(s) removed. Vehicles set to available.') % count
        
        # Show notification, close wizard, and force reload
        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
            'type': 'success',
            'title': _('Success'),
            'message': message,
            'sticky': False,
        })
        
        # Return reload action to force refresh the current view
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }