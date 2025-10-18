# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class VehicleCheckin(models.Model):
    _name = 'vehicle.checkin'
    _description = 'Vehicle Check-In/Check-Out'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enables chatter
    _order = 'checkin_date desc'
    _rec_name = 'display_name'
    
    # ========== BASIC FIELDS ==========
    display_name = fields.Char(
        string='Reference',
        compute='_compute_display_name',
        store=True
    )
    
    # ========== RELATIONAL FIELDS ==========
    driver_id = fields.Many2one(
        'res.partner',
        string='Driver',
        required=True,
        tracking=True,
        domain=[('is_company', '=', False)],  # Only individuals, not companies
        help="Driver assigned to this vehicle"
    )
    
    vehicle_id = fields.Many2one(
        'vehicle.vehicle',  # References vehicle_manager module
        string='Vehicle',
        required=True,
        tracking=True,
        help="Vehicle assigned to the driver"
    )
    
    # ========== DATE FIELDS ==========
    checkin_date = fields.Datetime(
        string='Check-In Date',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        help="Date and time when driver checked in"
    )
    
    checkout_date = fields.Datetime(
        string='Check-Out Date',
        tracking=True,
        help="Date and time when driver checked out"
    )
    
    # ========== STATUS FIELDS ==========
    state = fields.Selection([
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='checked_in', required=True, tracking=True)
    
    # ========== COMPUTED FIELDS ==========
    duration_hours = fields.Float(
        string='Duration (Hours)',
        compute='_compute_duration',
        store=True,
        help="Total hours the vehicle was used"
    )
    
    duration_days = fields.Float(
        string='Duration (Days)',
        compute='_compute_duration',
        store=True,
        help="Total days the vehicle was used"
    )
    
    is_checked_in = fields.Boolean(
        string='Currently Checked In',
        compute='_compute_is_checked_in',
        store=True
    )
    
    # ========== VEHICLE INFORMATION (Related Fields) ==========
    vehicle_license_plate = fields.Char(
        related='vehicle_id.license_plate',
        string='License Plate',
        store=True,
        readonly=True
    )
    
    vehicle_make = fields.Char(
        related='vehicle_id.make',
        string='Make',
        readonly=True
    )
    
    vehicle_model = fields.Char(
        related='vehicle_id.model',
        string='Model',
        readonly=True
    )
    
    # ========== ADDITIONAL FIELDS ==========
    notes = fields.Text(
        string='Notes',
        help="Additional notes or observations"
    )
    
    checkin_mileage = fields.Integer(
        string='Check-In Mileage',
        help="Vehicle mileage at check-in"
    )
    
    checkout_mileage = fields.Integer(
        string='Check-Out Mileage',
        help="Vehicle mileage at check-out"
    )
    
    distance_traveled = fields.Integer(
        string='Distance Traveled',
        compute='_compute_distance_traveled',
        store=True
    )
    
    # ========== COMPUTE METHODS ==========
    @api.depends('driver_id', 'vehicle_id', 'checkin_date')
    def _compute_display_name(self):
        """Generate display name for the record"""
        for record in self:
            if record.driver_id and record.vehicle_id:
                date_str = record.checkin_date.strftime('%Y-%m-%d') if record.checkin_date else ''
                record.display_name = f"{record.driver_id.name} - {record.vehicle_id.license_plate} ({date_str})"
            else:
                record.display_name = _("New Check-In")
    
    @api.depends('checkin_date', 'checkout_date')
    def _compute_duration(self):
        """Calculate duration between check-in and check-out"""
        for record in self:
            if record.checkout_date and record.checkin_date:
                delta = record.checkout_date - record.checkin_date
                record.duration_hours = delta.total_seconds() / 3600
                record.duration_days = delta.total_seconds() / 86400
            else:
                record.duration_hours = 0.0
                record.duration_days = 0.0
    
    @api.depends('state', 'checkout_date')
    def _compute_is_checked_in(self):
        """Check if the record is currently in checked-in state"""
        for record in self:
            record.is_checked_in = record.state == 'checked_in' and not record.checkout_date
    
    @api.depends('checkin_mileage', 'checkout_mileage')
    def _compute_distance_traveled(self):
        """Calculate distance traveled"""
        for record in self:
            if record.checkout_mileage and record.checkin_mileage:
                record.distance_traveled = record.checkout_mileage - record.checkin_mileage
            else:
                record.distance_traveled = 0
    
    # ========== CONSTRAINTS ==========
    @api.constrains('checkin_date', 'checkout_date')
    def _check_dates(self):
        """Validate that checkout date is after checkin date"""
        for record in self:
            if record.checkout_date and record.checkin_date:
                if record.checkout_date < record.checkin_date:
                    raise ValidationError(_("Check-out date must be after check-in date!"))
    
    @api.constrains('vehicle_id', 'state')
    def _check_vehicle_availability(self):
        """Ensure vehicle is available for check-in"""
        for record in self:
            if record.state == 'checked_in':
                # Check if vehicle is already checked in by another driver
                existing_checkin = self.search([
                    ('vehicle_id', '=', record.vehicle_id.id),
                    ('state', '=', 'checked_in'),
                    ('id', '!=', record.id),
                    ('checkout_date', '=', False)
                ], limit=1)
                
                if existing_checkin:
                    raise ValidationError(_(
                        "Vehicle %s is already checked in by %s!"
                    ) % (record.vehicle_id.license_plate, existing_checkin.driver_id.name))
    
    @api.constrains('checkin_mileage', 'checkout_mileage')
    def _check_mileage(self):
        """Validate mileage values"""
        for record in self:
            if record.checkout_mileage and record.checkin_mileage:
                if record.checkout_mileage < record.checkin_mileage:
                    raise ValidationError(_("Check-out mileage cannot be less than check-in mileage!"))
    
    # ========== CRUD METHODS ==========
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to update vehicle status on check-in"""
        records = super().create(vals_list)
        
        for record in records:
            if record.state == 'checked_in' and record.vehicle_id:
                # Update vehicle status to reserved
                record.vehicle_id.write({'status': 'reserved'})
                
                # Log message in chatter
                record.message_post(
                    body=_("Vehicle checked in by %s") % record.driver_id.name,
                    message_type='notification'
                )
        
        return records
    
    def write(self, vals):
        """Override write to handle status changes"""
        res = super().write(vals)
        
        # If checking out, update vehicle status
        if vals.get('state') == 'checked_out' or vals.get('checkout_date'):
            for record in self:
                if record.state == 'checked_out' and record.vehicle_id:
                    record.vehicle_id.write({'status': 'available'})
                    
                    # Log message in chatter
                    record.message_post(
                        body=_("Vehicle checked out by %s") % record.driver_id.name,
                        message_type='notification'
                    )
        
        return res
    
    def unlink(self):
        """Prevent deletion of checked-in records"""
        for record in self:
            if record.state == 'checked_in':
                raise UserError(_("Cannot delete a record that is currently checked in. Please check out first."))
        return super().unlink()
    
    # ========== ACTION METHODS ==========
    def action_checkout(self):
        """Action to check out - opens wizard"""
        self.ensure_one()
        
        if self.state != 'checked_in':
            raise UserError(_("This record is not in checked-in state!"))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Check-Out Vehicle'),
            'res_model': 'vehicle.checkout.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_checkin_id': self.id,
                'default_vehicle_id': self.vehicle_id.id,
                'default_driver_id': self.driver_id.id,
            }
        }
    
    def action_cancel(self):
        """Cancel the check-in"""
        self.ensure_one()
        
        if self.state == 'checked_out':
            raise UserError(_("Cannot cancel a completed check-out!"))
        
        # Make vehicle available again
        if self.vehicle_id and self.state == 'checked_in':
            self.vehicle_id.write({'status': 'available'})
        
        self.write({'state': 'cancelled'})
        
        self.message_post(
            body=_("Check-in cancelled"),
            message_type='notification'
        )
        
        return True
    
    def action_view_vehicle(self):
        """Open vehicle form view"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vehicle Details'),
            'res_model': 'vehicle.vehicle',
            'res_id': self.vehicle_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class VehicleVehicle(models.Model):
    """Extend vehicle.vehicle model from vehicle_manager"""
    _inherit = 'vehicle.vehicle'
    
    # Add reverse relationship
    checkin_ids = fields.One2many(
        'vehicle.checkin',
        'vehicle_id',
        string='Check-In History'
    )
    
    checkin_count = fields.Integer(
        string='Check-In Count',
        compute='_compute_checkin_count'
    )
    
    current_driver_id = fields.Many2one(
        'res.partner',
        string='Current Driver',
        compute='_compute_current_driver',
        store=False
    )
    
    @api.depends('checkin_ids')
    def _compute_checkin_count(self):
        """Count total check-ins for this vehicle"""
        for vehicle in self:
            vehicle.checkin_count = len(vehicle.checkin_ids)
    
    @api.depends('checkin_ids', 'checkin_ids.state')
    def _compute_current_driver(self):
        """Get current driver if vehicle is checked in"""
        for vehicle in self:
            active_checkin = self.env['vehicle.checkin'].search([
                ('vehicle_id', '=', vehicle.id),
                ('state', '=', 'checked_in'),
                ('checkout_date', '=', False)
            ], limit=1)
            
            vehicle.current_driver_id = active_checkin.driver_id if active_checkin else False
    
    def action_view_checkins(self):
        """View all check-ins for this vehicle"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Check-In History'),
            'res_model': 'vehicle.checkin',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }
