# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VehicleCheckinWizard(models.TransientModel):
    _name = 'vehicle.checkin.wizard'
    _description = 'Vehicle Check-In Wizard'
    
    driver_id = fields.Many2one(
        'res.partner',
        string='Driver',
        required=True,
        domain=[('is_company', '=', False)]
    )
    
    vehicle_id = fields.Many2one(
        'vehicle.vehicle',
        string='Vehicle',
        required=True,
        domain=[('status', '=', 'available')]  # Only available vehicles
    )
    
    checkin_date = fields.Datetime(
        string='Check-In Date',
        required=True,
        default=fields.Datetime.now
    )
    
    checkin_mileage = fields.Float(
        string='Current Mileage',
        digits=(12, 1),
        help="Vehicle mileage at check-in (from Fleet Manager)"
    )
    
    notes = fields.Text(string='Notes')
    
    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """Auto-populate mileage from vehicle when selected"""
        if self.vehicle_id:
            self.checkin_mileage = self.vehicle_id.mileage or 0.0
    
    def action_confirm_checkin(self):
        """Create check-in record and update vehicle status"""
        self.ensure_one()
        
        # Get mileage from vehicle if not set
        mileage = self.checkin_mileage
        if not mileage and self.vehicle_id:
            mileage = self.vehicle_id.mileage or 0.0
        
        # Create check-in record
        checkin = self.env['vehicle.checkin'].create({
            'driver_id': self.driver_id.id,
            'vehicle_id': self.vehicle_id.id,
            'checkin_date': self.checkin_date,
            'checkin_mileage': mileage,
            'notes': self.notes,
            'state': 'checked_in',
        })
        
        # Show success notification and close wizard (refreshes current view)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Vehicle %s checked in to %s') % (
                    self.vehicle_id.license_plate,
                    self.driver_id.name
                ),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
