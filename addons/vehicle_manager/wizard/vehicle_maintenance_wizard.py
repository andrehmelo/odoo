# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class VehicleMaintenanceWizard(models.TransientModel):
    _name = 'vehicle.maintenance.wizard'
    _description = 'Send Vehicle to Maintenance Wizard'

    vehicle_id = fields.Many2one(
        'vehicle.vehicle',
        string='Vehicle',
        required=True,
        readonly=True
    )
    
    license_plate = fields.Char(
        string='License Plate',
        related='vehicle_id.license_plate',
        readonly=True
    )
    
    entry_date = fields.Date(
        string='Entry Date',
        default=fields.Date.context_today,
        required=True,
        help="Date when the vehicle enters maintenance"
    )
    
    location = fields.Char(
        string='Maintenance Location',
        required=True,
        help="Location where the vehicle will be maintained"
    )
    
    description = fields.Text(
        string='Intervention Notes',
        required=True,
        help="Brief description of the reason for maintenance"
    )

    @api.constrains('entry_date')
    def _check_entry_date(self):
        """Validate entry date is not in the future beyond reasonable limit"""
        for record in self:
            if record.entry_date:
                today = fields.Date.context_today(record)
                if record.entry_date > today:
                    raise ValidationError(_("Entry date cannot be in the future."))

    def action_send_to_maintenance(self):
        """Send vehicle to maintenance and create intervention record"""
        self.ensure_one()
        
        # Validate vehicle is available
        if self.vehicle_id.status != 'available':
            raise ValidationError(_("Vehicle must be available to send to maintenance."))
        
        # Check if vehicle already has an active intervention
        active_intervention = self.vehicle_id.intervention_ids.filtered(
            lambda i: i.state == 'in_maintenance' and not i.exit_date
        )
        if active_intervention:
            raise ValidationError(_("Vehicle already has an active intervention in progress."))
        
        # Create intervention record
        intervention = self.env['car.intervention.history'].create({
            'vehicle_id': self.vehicle_id.id,
            'entry_date': self.entry_date,
            'location': self.location,
            'description': self.description,
            'state': 'in_maintenance'
        })
        
        # Update vehicle status
        self.vehicle_id.write({'status': 'maintenance'})
        
        # Show success message and close wizard
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Vehicle %s has been sent to maintenance.') % self.vehicle_id.name,
                'type': 'success',
                'sticky': False,
            }
        }


class VehicleAvailableWizard(models.TransientModel):
    _name = 'vehicle.available.wizard'
    _description = 'Send Vehicle to Available Wizard'

    vehicle_id = fields.Many2one(
        'vehicle.vehicle',
        string='Vehicle',
        required=True,
        readonly=True
    )
    
    license_plate = fields.Char(
        string='License Plate',
        related='vehicle_id.license_plate',
        readonly=True
    )
    
    current_intervention_id = fields.Many2one(
        'car.intervention.history',
        string='Current Intervention',
        compute='_compute_current_intervention',
        readonly=True
    )
    
    entry_date = fields.Date(
        string='Entry Date',
        related='current_intervention_id.entry_date',
        readonly=True
    )
    
    exit_date = fields.Date(
        string='Exit Date',
        default=fields.Date.context_today,
        required=True,
        help="Date when the vehicle left maintenance"
    )
    
    location = fields.Char(
        string='Maintenance Location',
        related='current_intervention_id.location',
        readonly=True
    )
    
    description = fields.Text(
        string='Intervention Notes',
        related='current_intervention_id.description',
        readonly=False,
        help="Final notes about what was done during maintenance"
    )
    
    days_in_maintenance = fields.Integer(
        string='Days in Maintenance',
        compute='_compute_days_in_maintenance',
        readonly=True
    )

    @api.depends('vehicle_id')
    def _compute_current_intervention(self):
        """Find the current active intervention"""
        for record in self:
            current_intervention = record.vehicle_id.intervention_ids.filtered(
                lambda i: i.state == 'in_maintenance' and not i.exit_date
            )
            record.current_intervention_id = current_intervention[0] if current_intervention else False

    @api.depends('entry_date', 'exit_date')
    def _compute_days_in_maintenance(self):
        """Calculate days in maintenance"""
        for record in self:
            if record.entry_date and record.exit_date:
                delta = record.exit_date - record.entry_date
                record.days_in_maintenance = delta.days
            else:
                record.days_in_maintenance = 0

    @api.constrains('exit_date')
    def _check_exit_date(self):
        """Validate exit date is not before entry date"""
        for record in self:
            if record.exit_date and record.entry_date:
                if record.exit_date < record.entry_date:
                    raise ValidationError(_("Exit date cannot be earlier than entry date (%s).") % record.entry_date)

    def action_send_to_available(self):
        """Send vehicle to available and close intervention record"""
        self.ensure_one()
        
        # Validate vehicle is in maintenance
        if self.vehicle_id.status != 'maintenance':
            raise ValidationError(_("Vehicle must be in maintenance to send to available."))
        
        # Validate we have a current intervention
        if not self.current_intervention_id:
            raise ValidationError(_("No active intervention found for this vehicle."))
        
        # Validate exit date is provided
        if not self.exit_date:
            raise ValidationError(_("Exit date is required to complete the intervention."))
        
        # Update intervention record
        self.current_intervention_id.write({
            'exit_date': self.exit_date,
            'description': self.description,
            'state': 'completed'
        })
        
        # Update vehicle status
        self.vehicle_id.write({'status': 'available'})
        
        # Show success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Vehicle %s is now available. Intervention completed after %d days.') % (
                    self.vehicle_id.name, self.days_in_maintenance
                ),
                'type': 'success',
                'sticky': False,
            }
        }