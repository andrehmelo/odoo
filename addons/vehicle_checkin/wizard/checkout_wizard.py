# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VehicleCheckoutWizard(models.TransientModel):
    _name = 'vehicle.checkout.wizard'
    _description = 'Vehicle Check-Out Wizard'
    
    checkin_id = fields.Many2one(
        'vehicle.checkin',
        string='Check-In Record',
        required=True,
        readonly=True
    )
    
    vehicle_id = fields.Many2one(
        'vehicle.vehicle',
        string='Vehicle',
        required=True,
        readonly=True
    )
    
    driver_id = fields.Many2one(
        'res.partner',
        string='Driver',
        required=True,
        readonly=True
    )
    
    checkout_date = fields.Datetime(
        string='Check-Out Date',
        required=True,
        default=fields.Datetime.now
    )
    
    checkout_mileage = fields.Integer(
        string='Current Mileage',
        help="Vehicle mileage at check-out"
    )
    
    notes = fields.Text(string='Notes')
    
    fuel_level = fields.Selection([
        ('empty', 'Empty'),
        ('quarter', '1/4 Tank'),
        ('half', '1/2 Tank'),
        ('three_quarters', '3/4 Tank'),
        ('full', 'Full Tank')
    ], string='Fuel Level at Return')
    
    vehicle_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged')
    ], string='Vehicle Condition')
    
    damage_description = fields.Text(
        string='Damage Description',
        help="Describe any damage or issues found"
    )
    
    @api.constrains('checkout_date', 'checkin_id')
    def _check_checkout_date(self):
        """Ensure checkout date is after checkin date"""
        for record in self:
            if record.checkin_id and record.checkout_date < record.checkin_id.checkin_date:
                raise ValidationError(_("Check-out date must be after check-in date!"))
    
    def action_confirm_checkout(self):
        """Process check-out"""
        self.ensure_one()
        
        # Update check-in record
        self.checkin_id.write({
            'checkout_date': self.checkout_date,
            'checkout_mileage': self.checkout_mileage,
            'state': 'checked_out',
            'notes': f"{self.checkin_id.notes or ''}\n\nCheck-out notes:\n{self.notes or ''}" if self.notes else self.checkin_id.notes,
        })
        
        # Log checkout information in chatter
        message = _("Vehicle checked out\n")
        if self.fuel_level:
            message += _("Fuel Level: %s\n") % dict(self._fields['fuel_level'].selection).get(self.fuel_level)
        if self.vehicle_condition:
            message += _("Condition: %s\n") % dict(self._fields['vehicle_condition'].selection).get(self.vehicle_condition)
        if self.damage_description:
            message += _("Damage: %s\n") % self.damage_description
        
        self.checkin_id.message_post(body=message, message_type='comment')
        
        # Show success notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Vehicle %s checked out successfully') % self.vehicle_id.license_plate,
                'type': 'success',
                'next': {'type': 'ir.actions.client', 'tag': 'reload'}
            }
        }
