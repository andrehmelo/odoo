# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VehicleDeleteWizard(models.TransientModel):
    _name = 'vehicle.delete.wizard'
    _description = 'Vehicle Delete Wizard'

    delete_type = fields.Selection([
        ('all', 'Delete All Vehicles'),
        ('available', 'Delete Available Vehicles'),
        ('reserved', 'Delete Reserved Vehicles'),
        ('maintenance', 'Delete Maintenance Vehicles'),
    ], string='Delete Option', required=True, default='all')
    
    confirm_delete = fields.Boolean(
        string='I confirm I want to delete the vehicles',
        help="Check this box to confirm the deletion"
    )
    
    vehicle_count = fields.Integer(
        string='Vehicles to Delete',
        compute='_compute_vehicle_count'
    )

    @api.depends('delete_type')
    def _compute_vehicle_count(self):
        """Calculate how many vehicles will be deleted"""
        for wizard in self:
            domain = []
            if wizard.delete_type != 'all':
                domain = [('status', '=', wizard.delete_type)]
            
            wizard.vehicle_count = self.env['vehicle.vehicle'].search_count(domain)

    def action_delete_vehicles(self):
        """Delete vehicles based on selected criteria"""
        if not self.confirm_delete:
            raise UserError(_("Please confirm the deletion by checking the confirmation box."))
        
        # Build domain based on delete_type
        domain = []
        if self.delete_type != 'all':
            domain = [('status', '=', self.delete_type)]
        
        # Find vehicles to delete
        vehicles_to_delete = self.env['vehicle.vehicle'].search(domain)
        
        if not vehicles_to_delete:
            raise UserError(_("No vehicles found matching the selected criteria."))
        
        count = len(vehicles_to_delete)
        
        # Delete the vehicles
        vehicles_to_delete.unlink()
        
        # Show success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%d vehicle(s) have been successfully deleted.') % count,
                'type': 'success',
                'sticky': False,
            }
        }