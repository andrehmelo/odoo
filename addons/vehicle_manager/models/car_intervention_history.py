# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class CarInterventionHistory(models.Model):
    _name = 'car.intervention.history'
    _description = 'Car Intervention History'
    _order = 'entry_date desc, id desc'
    _rec_name = 'display_name'

    # Relationship to vehicle
    vehicle_id = fields.Many2one(
        'vehicle.vehicle',
        string='Vehicle',
        required=True,
        ondelete='cascade',
        help="The vehicle that is going to maintenance"
    )
    
    # Fields from vehicle table
    license_plate = fields.Char(
        string='License Plate',
        related='vehicle_id.license_plate',
        store=True,
        readonly=True,
        help="License plate of the vehicle"
    )
    
    location = fields.Char(
        string='Maintenance Location',
        help="Location where the vehicle is being maintained"
    )
    
    # Intervention specific fields
    entry_date = fields.Date(
        string='Entry Date',
        default=fields.Date.context_today,
        required=True,
        help="Date when the vehicle entered maintenance"
    )
    
    exit_date = fields.Date(
        string='Exit Date',
        help="Date when the vehicle left maintenance (empty while still in maintenance)"
    )
    
    description = fields.Text(
        string='Intervention Notes',
        help="Brief description of the accident or motive for maintenance"
    )
    
    # Status field to track intervention state
    state = fields.Selection([
        ('in_maintenance', 'In Maintenance'),
        ('completed', 'Completed'),
    ], string='Status', default='in_maintenance', required=True)
    
    # Computed fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    days_in_maintenance = fields.Integer(
        string='Days in Maintenance',
        compute='_compute_days_in_maintenance',
        help="Number of days the vehicle has been/was in maintenance"
    )
    
    is_active_intervention = fields.Boolean(
        string='Active Intervention',
        compute='_compute_is_active_intervention',
        store=True,
        help="True if this is an ongoing intervention (no exit date)"
    )

    @api.depends('vehicle_id', 'entry_date', 'state')
    def _compute_display_name(self):
        for record in self:
            if record.vehicle_id and record.entry_date:
                record.display_name = f"{record.vehicle_id.license_plate} - {record.entry_date} ({record.state})"
            else:
                record.display_name = "New Intervention"

    @api.depends('entry_date', 'exit_date')
    def _compute_days_in_maintenance(self):
        for record in self:
            if record.entry_date:
                end_date = record.exit_date or fields.Date.context_today(record)
                delta = end_date - record.entry_date
                record.days_in_maintenance = delta.days
            else:
                record.days_in_maintenance = 0

    @api.depends('exit_date')
    def _compute_is_active_intervention(self):
        for record in self:
            record.is_active_intervention = not bool(record.exit_date)

    @api.constrains('entry_date', 'exit_date')
    def _check_dates(self):
        for record in self:
            if record.exit_date and record.entry_date and record.exit_date < record.entry_date:
                raise ValidationError("Exit date cannot be earlier than entry date.")

    def action_create_intervention(self):
        """Action for creating a new intervention from the form"""
        self.ensure_one()
        
        # Validate required fields
        if not self.vehicle_id or not self.entry_date or not self.location or not self.description:
            raise ValidationError("All fields are required to send a vehicle to maintenance.")
        
        # Validate vehicle is available
        if self.vehicle_id.status != 'available':
            raise ValidationError("Vehicle must be available to send to maintenance.")
        
        # Check if vehicle already has an active intervention
        active_intervention = self.vehicle_id.intervention_ids.filtered(
            lambda i: i.state == 'in_maintenance' and not i.exit_date and i.id != self.id
        )
        if active_intervention:
            raise ValidationError("Vehicle already has an active intervention in progress.")
        
        # If this is a new record (NewId), it needs to be created properly
        if not self.id or isinstance(self.id, models.NewId):
            # Create the intervention record
            vals = {
                'vehicle_id': self.vehicle_id.id,
                'entry_date': self.entry_date,
                'location': self.location,
                'description': self.description,
                'state': 'in_maintenance',
            }
            new_intervention = self.create(vals)
            # Update vehicle status
            new_intervention.vehicle_id.write({'status': 'maintenance'})
        else:
            # Update existing record
            self.write({
                'state': 'in_maintenance',
            })
            # Update vehicle status
            self.vehicle_id.write({'status': 'maintenance'})
        
        # Return action to close form and go back to list
        return {
            'type': 'ir.actions.act_window_close',
        }

    def action_complete_intervention(self):
        """Action for completing an active intervention from the form"""
        self.ensure_one()
        
        # Validate exit date is set
        if not self.exit_date:
            raise ValidationError("Exit date is required to complete the maintenance intervention.")
        
        # Validate exit date is not before entry date
        if self.exit_date < self.entry_date:
            raise ValidationError("Exit date cannot be earlier than entry date.")
        
        # Update record state
        self.write({
            'state': 'completed',
        })
        
        # Update vehicle status
        if self.vehicle_id:
            self.vehicle_id.write({'status': 'available'})
        
        # Return action to close form and go back to list
        return {
            'type': 'ir.actions.act_window_close',
        }