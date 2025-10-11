# -*- coding: utf-8 -*-

from odoo import models, fields, api
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

    @api.onchange('exit_date')
    def _onchange_exit_date(self):
        """Update state when exit date is set"""
        for record in self:
            if record.exit_date:
                record.state = 'completed'
            else:
                record.state = 'in_maintenance'

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle vehicle state change"""
        interventions = super().create(vals_list)
        # When creating a new intervention, update vehicle state to maintenance
        for intervention in interventions:
            if intervention.vehicle_id:
                intervention.vehicle_id.status = 'maintenance'
        return interventions

    def write(self, vals):
        """Override write to handle vehicle state changes"""
        result = super().write(vals)
        
        # If exit_date is being set, update vehicle state to available
        if 'exit_date' in vals and vals['exit_date']:
            for record in self:
                if record.vehicle_id:
                    record.vehicle_id.status = 'available'
                    
        return result

    @api.constrains('entry_date', 'exit_date')
    def _check_dates(self):
        for record in self:
            if record.exit_date and record.entry_date and record.exit_date < record.entry_date:
                raise ValueError("Exit date cannot be earlier than entry date.")