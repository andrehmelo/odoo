# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class Vehicle(models.Model):
    _name = 'vehicle.vehicle'
    _description = 'Vehicle'
    _order = 'name desc, id desc'
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
        string='VIN (Vehicle Identification Number)',
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
    body_type = fields.Selection([
        ('sedan', 'Sedan'),
        ('hatchback', 'Hatchback'),
        ('suv', 'SUV'),
        ('truck', 'Truck'),
        ('coupe', 'Coupe'),
        ('convertible', 'Convertible'),
        ('wagon', 'Station Wagon'),
        ('van', 'Van'),
        ('motorcycle', 'Motorcycle'),
        ('other', 'Other'),
    ], string='Body Type')
    
    doors = fields.Integer(
        string='Number of Doors',
        help="Number of doors (2, 4, etc.)"
    )
    seats = fields.Integer(
        string='Seating Capacity',
        help="Number of seats/passengers"
    )
    
    # Engine & Performance
    engine_size = fields.Float(
        string='Engine Size (L)',
        digits=(4, 1),
        help="Engine displacement in liters"
    )
    engine_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
        ('other', 'Other'),
    ], string='Fuel Type')
    
    transmission = fields.Selection([
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('cvt', 'CVT'),
        ('semi_automatic', 'Semi-Automatic'),
    ], string='Transmission')
    
    drivetrain = fields.Selection([
        ('fwd', 'Front-Wheel Drive (FWD)'),
        ('rwd', 'Rear-Wheel Drive (RWD)'),
        ('awd', 'All-Wheel Drive (AWD)'),
        ('4wd', '4-Wheel Drive (4WD)'),
    ], string='Drivetrain')
    
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
    
    condition = fields.Selection([
        ('new', 'New'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ], string='Condition', default='good')
    
    # Financial Information
    purchase_price = fields.Monetary(
        string='Purchase Price',
        currency_field='currency_id',
        help="Price paid when vehicle was acquired"
    )
    current_value = fields.Monetary(
        string='Current Value',
        currency_field='currency_id',
        help="Current estimated market value"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Status & Availability
    status = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('maintenance', 'In Maintenance'),
    ], string='Status', default='available', required=True)
    
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
        """Set vehicle status to available"""
        self.write({'status': 'available'})
    
    def action_set_reserved(self):
        """Set vehicle status to reserved"""
        self.write({'status': 'reserved'})
    

    
    def action_set_maintenance(self):
        """Set vehicle status to maintenance"""
        self.write({'status': 'maintenance'})
    
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