# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class Vehicle(models.Model):
    _name = 'vehicle.vehicle'
    _description = 'Vehicle'
    _order = 'sequence, name desc, id desc'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Basic Information
    name = fields.Char(
        string='Vehicle Name', 
        compute='_compute_name', 
        store=True,
        help="Auto-generated name based on make, model and year"
    )
    make = fields.Char(
        string='Make/Brand', 
        required=True, 
        help="Vehicle manufacturer (e.g., Toyota, Ford, BMW)"
    )
    model = fields.Char(
        string='Model', 
        required=True,
        help="Vehicle model (e.g., Camry, F-150, 3 Series)"
    )
    year = fields.Integer(
        string='Year', 
        required=True,
        help="Manufacturing year"
    )
    
    # Identification
    vin = fields.Char(
        string='VIN',
        size=17,
        help="17-character Vehicle Identification Number"
    )
    license_plate = fields.Char(
        string='License Plate',
        help="Current license plate number"
    )
    
    # Physical Characteristics  
    color = fields.Char(
        string='Color',
        help="Primary exterior color"
    )
    
    # Mileage & Condition
    mileage = fields.Float(
        string='Mileage',
        digits=(12, 1),
        help="Current odometer reading"
    )
    mileage_unit = fields.Selection([
        ('km', 'Kilometers'),
        ('miles', 'Miles'),
    ], string='Mileage Unit', default='km')
    
    # Car Details & Equipment
    via_verde_card = fields.Integer(
        string='Via Verde Card',
        help="Via Verde card number for highway tolls and parking payments"
    )
    gas_card = fields.Integer(
        string='Gas Card',
        help="Gas payment card number associated with this vehicle"
    )
    fire_extinguisher = fields.Integer(
        string='Fire Extinguisher ID',
        help="Fire extinguisher identification number for this car"
    )
    insurance_date = fields.Date(
        string='Insurance Expiry',
        help="Car insurance expiration date"
    )
    ipo_date = fields.Date(
        string='IPO Expiry',
        help="Car IPO (inspection) expiration date"
    )
    
    condition = fields.Selection([
        ('new', 'New'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ], string='Condition', default='good')
    
    # Financial Information
    purchase_price = fields.Float(
        string='Purchase Price (€)',
        digits=(12, 2),
        help="Price paid when vehicle was acquired in Euros"
    )
    current_value = fields.Float(
        string='Current Value (€)',
        digits=(12, 2),
        help="Current estimated market value in Euros"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Driver Fees Information
    weekly_rent = fields.Float(
        string='Weekly Rent (€)',
        digits=(8, 2),
        help="Amount driver pays per week to rent this vehicle in Euros"
    )
    entry_deposit = fields.Float(
        string='Entry Deposit (€)',
        digits=(8, 2),
        help="Upfront deposit paid by driver, reimbursed when returning car in good condition in Euros"
    )
    reserve_fee = fields.Float(
        string='Reserve Fee (€)',
        digits=(8, 2),
        help="Weekly fee deducted from driver's paycheck, returned when car is returned in Euros"
    )
    reserve_fee_max = fields.Float(
        string='Reserve Fee Max (€)',
        digits=(8, 2),
        help="Maximum amount of reserve fee that can be accumulated in Euros"
    )
    
    # Status & Availability
    status = fields.Selection([
        ('available', 'Available'), 
        ('reserved', 'Reserved'),
        ('maintenance', 'In Maintenance'),
    ], string='Status', default='available', required=True)
    
    # Sequence field for drag & drop ordering
    sequence = fields.Integer(string='Sequence', default=10, help="Used for ordering vehicles in kanban view")
    
    # Dates
    purchase_date = fields.Date(
        string='Purchase Date',
        help="Date when vehicle was acquired"
    )

    
    # Additional Information
    description = fields.Text(
        string='Description',
        help="General description of the vehicle"
    )
    notes = fields.Text(
        string='Notes',
        help="Additional notes about the vehicle"
    )
    features = fields.Text(
        string='Features & Options',
        help="Special features, options, and equipment"
    )
    
    # Location
    location = fields.Char(
        string='Current Location',
        help="Current physical location of the vehicle"
    )
    
    # Contact Information (if applicable)
    owner_id = fields.Many2one(
        'res.partner',
        string='Owner/Contact',
        help="Current owner or contact person"
    )
    
    # Intervention History Relationship
    intervention_ids = fields.One2many(
        'car.intervention.history',
        'vehicle_id',
        string='Intervention History',
        help="History of maintenance interventions for this vehicle"
    )
    
    current_intervention_id = fields.Many2one(
        'car.intervention.history',
        string='Current Intervention',
        compute='_compute_current_intervention',
        store=True,
        help="Current active intervention (if vehicle is in maintenance)"
    )
    
    # Related fields from current intervention
    current_intervention_entry_date = fields.Date(
        string='Entry Date',
        related='current_intervention_id.entry_date',
        readonly=True,
        help="Date when vehicle entered maintenance"
    )
    
    current_intervention_days = fields.Integer(
        string='Days in Maintenance',
        related='current_intervention_id.days_in_maintenance',
        readonly=True,
        help="Number of days in maintenance"
    )
    
    current_intervention_location = fields.Char(
        string='Maintenance Location',
        related='current_intervention_id.location',
        readonly=True,
        help="Where the vehicle is being maintained"
    )
    
    current_intervention_notes = fields.Text(
        string='Intervention Notes',
        related='current_intervention_id.description',
        readonly=True,
        help="Details about the intervention"
    )
    
    # Computed fields
    age = fields.Integer(
        string='Age (Years)',
        compute='_compute_age',
        help="Vehicle age in years"
    )
    
    # Active field for archiving
    active = fields.Boolean(default=True)
    
    @api.depends('make', 'model', 'year')
    def _compute_name(self):
        """Generate vehicle name from make, model and year"""
        for vehicle in self:
            if vehicle.make and vehicle.model:
                if vehicle.year:
                    vehicle.name = f"{vehicle.year} {vehicle.make} {vehicle.model}"
                else:
                    vehicle.name = f"{vehicle.make} {vehicle.model}"
            else:
                vehicle.name = "New Vehicle"
    
    @api.depends('year')
    def _compute_age(self):
        """Calculate vehicle age"""
        current_year = fields.Date.today().year
        for vehicle in self:
            if vehicle.year:
                vehicle.age = max(0, current_year - vehicle.year)
            else:
                vehicle.age = 0
    
    # Audit Information (computed fields)
    created_by_name = fields.Char(
        string='Created By',
        compute='_compute_audit_info',
        help="Name of the user who created this vehicle record"
    )
    last_modified_by_name = fields.Char(
        string='Last Modified By', 
        compute='_compute_audit_info',
        help="Name of the user who last modified this vehicle record"
    )
    
    @api.depends('create_uid', 'write_uid')
    def _compute_audit_info(self):
        """Compute audit information - who created and last modified the record"""
        for vehicle in self:
            # Created by
            if vehicle.create_uid:
                vehicle.created_by_name = vehicle.create_uid.name
            else:
                vehicle.created_by_name = 'Unknown'
                
            # Last modified by
            if vehicle.write_uid:
                vehicle.last_modified_by_name = vehicle.write_uid.name
            else:
                vehicle.last_modified_by_name = 'Unknown'
    
    @api.depends('intervention_ids.state')
    def _compute_current_intervention(self):
        """Find the current active intervention for this vehicle"""
        for vehicle in self:
            current_intervention = vehicle.intervention_ids.filtered(
                lambda i: i.state == 'in_maintenance' and not i.exit_date
            )
            vehicle.current_intervention_id = current_intervention[0] if current_intervention else False
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle VIN normalization and set default year"""
        for vals in vals_list:
            # Handle VIN normalization
            if vals.get('vin'):
                vals['vin'] = vals['vin'].upper()
                
            # If no year is provided, try to extract from model or set default
            if not vals.get('year'):
                model_name = vals.get('model', '')
                # Try to extract year from model string
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', model_name)
                if year_match:
                    vals['year'] = int(year_match.group())
                else:
                    # Set a reasonable default year
                    vals['year'] = 2020
        
        return super().create(vals_list)
    
    @api.constrains('vin')
    def _check_vin(self):
        """Validate VIN format and uniqueness"""
        for vehicle in self:
            if vehicle.vin:
                # Check VIN length (should be 17 characters)
                if len(vehicle.vin) != 17:
                    raise ValidationError(_("VIN must be exactly 17 characters long."))
                
                # Check VIN format (letters and numbers only, exclude I, O, Q)
                if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vehicle.vin.upper()):
                    raise ValidationError(_("VIN contains invalid characters. Only letters (excluding I, O, Q) and numbers are allowed."))
                
                # Check uniqueness
                existing = self.search([('vin', '=', vehicle.vin), ('id', '!=', vehicle.id)])
                if existing:
                    raise ValidationError(_("VIN must be unique. This VIN already exists for vehicle: %s") % existing.name)
    
    @api.constrains('year')
    def _check_year(self):
        """Validate year is reasonable"""
        current_year = fields.Date.today().year
        for vehicle in self:
            if vehicle.year:
                if vehicle.year < 1900 or vehicle.year > current_year + 1:
                    raise ValidationError(_("Year must be between 1900 and %s") % (current_year + 1))
    
    @api.constrains('mileage')
    def _check_mileage(self):
        """Validate mileage is not negative"""
        for vehicle in self:
            if vehicle.mileage < 0:
                raise ValidationError(_("Mileage cannot be negative."))
    
    def action_set_available(self):
        """Open wizard to set vehicle status to available"""
        self.ensure_one()
        
        # Check if vehicle is in maintenance
        if self.status != 'maintenance':
            raise ValidationError(_("Vehicle must be in maintenance to use this action."))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Set Vehicle Available',
            'res_model': 'vehicle.available.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_vehicle_id': self.id},
        }
    
    def action_set_reserved(self):
        """Set vehicle status to reserved"""
        self.write({'status': 'reserved'})
    
    def action_set_maintenance(self):
        """Open wizard to set vehicle status to maintenance"""
        self.ensure_one()
        
        # Check if vehicle is available
        if self.status != 'available':
            raise ValidationError(_("Vehicle must be available to send to maintenance."))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Vehicle to Maintenance',
            'res_model': 'vehicle.maintenance.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_vehicle_id': self.id},
        }
    
    def action_open_delete_wizard(self):
        """Open the delete wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delete Vehicles',
            'res_model': 'vehicle.delete.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {},
        }
    
    def name_get(self):
        """Custom name display"""
        result = []
        for vehicle in self:
            name = vehicle.name
            if vehicle.license_plate:
                name += f" ({vehicle.license_plate})"
            result.append((vehicle.id, name))
        return result
    

    
    def write(self, vals):
        """Override write to handle VIN normalization"""
        if vals.get('vin'):
            vals['vin'] = vals['vin'].upper()
        
        return super().write(vals)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Override read_group to ensure all status groups are shown"""
        result = super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)
        
        if groupby and 'status' in groupby[0]:
            # Ensure all status groups exist, even if empty
            existing_statuses = {group.get('status') for group in result if 'status' in group}
            all_statuses = ['available', 'reserved', 'maintenance']
            
            for status in all_statuses:
                if status not in existing_statuses:
                    # Add empty group
                    empty_group = {
                        'status': status,
                        'status_count': 0,
                        '__domain': [('status', '=', status)] + domain,
                        '__context': {'group_by': groupby[1:] if len(groupby) > 1 else []}
                    }
                    # Set the count field name
                    if fields:
                        for field in fields:
                            if field != 'status':
                                empty_group[field] = 0
                    result.append(empty_group)
            
            # Sort to maintain consistent order
            status_order = {'available': 0, 'reserved': 1, 'maintenance': 2}
            result.sort(key=lambda x: status_order.get(x.get('status'), 999))
        
        return result
    
    @api.model
    def _init_sequence_values(self):
        """Initialize sequence values for existing records"""
        vehicles_without_sequence = self.search([('sequence', '=', 0)])
        for i, vehicle in enumerate(vehicles_without_sequence):
            vehicle.sequence = (i + 1) * 10

    def action_set_maintenance(self):
        """Action to send vehicle to maintenance - shows wizard for maintenance vehicles"""
        if self.status != 'available':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Vehicle is currently {self.status}. Only available vehicles can be sent to maintenance.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        return {
            'name': 'Send to Maintenance',
            'type': 'ir.actions.act_window',
            'res_model': 'vehicle.maintenance.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('vehicle_manager.view_vehicle_maintenance_wizard_form').id,
            'target': 'new',
            'context': {
                'default_vehicle_id': self.id,
                'default_new_status': 'maintenance',
            }
        }

    def action_set_available(self):
        """Action to set vehicle as available - shows wizard when coming from maintenance"""
        if self.status == 'maintenance':
            # Show wizard for maintenance to available transition
            return {
                'name': 'Set as Available',
                'type': 'ir.actions.act_window',
                'res_model': 'vehicle.available.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('vehicle_manager.view_vehicle_available_wizard_form').id,
                'target': 'new',
                'context': {
                    'default_vehicle_id': self.id,
                    'default_new_status': 'available',
                }
            }
        else:
            # Simple status change for other transitions
            self.write({'status': 'available'})
            return True

    def action_set_reserved(self):
        """Action to set vehicle as reserved - simple status change"""
        if self.status == 'maintenance':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Vehicles in maintenance cannot be reserved directly. Please set as available first.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        self.write({'status': 'reserved'})
        return True

    def open_form_view(self):
        """Action to open the vehicle form view"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vehicle.vehicle',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'current',
        }

    def action_delete_vehicle(self):
        """Action to delete the vehicle (only when available)"""
        from odoo.exceptions import ValidationError
        
        self.ensure_one()
        
        # Validate vehicle is available
        if self.status != 'available':
            raise ValidationError("Only available vehicles can be deleted. Please set the vehicle as available first or remove the active maintenance.")
        
        # Store vehicle info for the notification
        vehicle_name = self.display_name
        
        # Delete the vehicle (cascade will handle related records)
        self.unlink()
        
        # Return to the fleet overview (kanban view) using the menu action
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fleet Overview',
            'res_model': 'vehicle.vehicle',
            'view_mode': 'kanban,tree,form',
            'views': [(False, 'kanban'), (False, 'tree'), (False, 'form')],
            'target': 'current',
            'domain': [],
            'context': {}
        }

    def action_remove_maintenance(self):
        """Action to remove current maintenance and set vehicle as available"""
        from odoo.exceptions import ValidationError
        
        self.ensure_one()
        
        # Validate vehicle is in maintenance
        if self.status != 'maintenance':
            raise ValidationError("Vehicle is not in maintenance.")
        
        # Get the current active intervention
        if not self.current_intervention_id:
            raise ValidationError("No active intervention found for this vehicle.")
        
        intervention_name = self.current_intervention_id.display_name
        
        # Delete the intervention
        self.current_intervention_id.unlink()
        
        # Set vehicle as available
        self.write({'status': 'available'})
        
        # Return True to refresh the current view in place (like action_set_maintenance does)
        return True