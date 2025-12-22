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
        'drivers.management',
        string='Driver',
        required=True,
        readonly=True
    )
    
    checkout_date = fields.Datetime(
        string='Check-Out Date',
        required=True,
        default=fields.Datetime.now
    )
    
    checkout_mileage = fields.Float(
        string='Current Mileage',
        digits=(12, 1),
        required=True,
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
    
    @api.constrains('checkout_mileage', 'checkin_id')
    def _check_mileage(self):
        """Ensure checkout mileage is greater than or equal to checkin mileage"""
        for record in self:
            if record.checkout_mileage and record.checkin_id and record.checkin_id.checkin_mileage:
                if record.checkout_mileage < record.checkin_id.checkin_mileage:
                    raise ValidationError(
                        _("Check-out mileage (%.1f) cannot be less than check-in mileage (%.1f)!") % 
                        (record.checkout_mileage, record.checkin_id.checkin_mileage)
                    )
    
    def action_confirm_checkout(self):
        """Process check-out"""
        self.ensure_one()
        
        # Build notes with additional information
        checkout_notes = []
        if self.fuel_level:
            checkout_notes.append(_("Fuel Level: %s") % dict(self._fields['fuel_level'].selection).get(self.fuel_level))
        if self.vehicle_condition:
            checkout_notes.append(_("Condition: %s") % dict(self._fields['vehicle_condition'].selection).get(self.vehicle_condition))
        if self.damage_description:
            checkout_notes.append(_("Damage: %s") % self.damage_description)
        
        # Combine with existing notes
        combined_notes = self.checkin_id.notes or ''
        if self.notes or checkout_notes:
            combined_notes += "\n\n--- Check-out Information ---\n"
            if checkout_notes:
                combined_notes += "\n".join(checkout_notes) + "\n"
            if self.notes:
                combined_notes += self.notes
        
        # Update check-in record
        self.checkin_id.write({
            'checkout_date': self.checkout_date,
            'checkout_mileage': self.checkout_mileage,
            'state': 'checked_out',
            'notes': combined_notes,
        })
        
        # Update vehicle mileage in fleet manager
        if self.checkout_mileage:
            self.vehicle_id.write({
                'mileage': self.checkout_mileage
            })
        
        # Show success notification and return to dashboard
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Vehicle %s checked out successfully') % self.vehicle_id.license_plate,
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.client',
                    'tag': 'vehicle_checkin_dashboard',
                }
            }
        }
