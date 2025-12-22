# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VehicleExtended(models.Model):
    _inherit = 'vehicle.vehicle'
    
    # Driver Check-In History Relationship
    checkin_ids = fields.One2many(
        'vehicle.checkin',
        'vehicle_id',
        string='Driver History',
        help="History of driver check-ins and check-outs for this vehicle"
    )
    
    # Current Check-In Information
    current_checkin_id = fields.Many2one(
        'vehicle.checkin',
        string='Current Check-In',
        compute='_compute_current_checkin',
        store=True,
        help="Current active check-in (if vehicle is reserved)"
    )
    
    # Related fields from current check-in
    current_checkin_driver_id = fields.Many2one(
        'drivers.management',
        string='Checked-In Driver',
        related='current_checkin_id.driver_id',
        readonly=True,
        help="Driver currently assigned to this vehicle"
    )
    
    current_checkin_date = fields.Datetime(
        string='Check-In Date',
        related='current_checkin_id.checkin_date',
        readonly=True,
        help="Date and time when driver checked in"
    )
    
    current_checkin_mileage = fields.Float(
        string='Check-In Mileage',
        related='current_checkin_id.checkin_mileage',
        readonly=True,
        help="Vehicle mileage at check-in"
    )
    
    current_checkin_duration_days = fields.Float(
        string='Days Checked Out',
        related='current_checkin_id.duration_days',
        readonly=True,
        help="Number of days since check-in"
    )
    
    @api.depends('checkin_ids.state')
    def _compute_current_checkin(self):
        """Find the current active check-in for this vehicle"""
        for vehicle in self:
            current_checkin = vehicle.checkin_ids.filtered(
                lambda c: c.state == 'checked_in' and not c.checkout_date
            )
            vehicle.current_checkin_id = current_checkin[0] if current_checkin else False
    
    def unlink(self):
        """Before deleting vehicles, clean up active check-ins and reset drivers"""
        for vehicle in self:
            # Find active check-ins for this vehicle
            active_checkins = self.env['vehicle.checkin'].search([
                ('vehicle_id', '=', vehicle.id),
                ('state', '=', 'checked_in'),
            ])
            
            for checkin in active_checkins:
                # Reset driver to inactive and clear vehicle
                if checkin.driver_id:
                    checkin.driver_id.write({
                        'status': 'inactive',
                        'vehicle_id': False,
                    })
                # Cancel the check-in (don't delete, keep history)
                checkin.write({'state': 'cancelled'})
        
        return super().unlink()
