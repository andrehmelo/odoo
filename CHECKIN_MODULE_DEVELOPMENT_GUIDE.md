# Vehicle Check-In/Check-Out Module Development Guide

## Overview
This guide provides complete instructions for building a **vehicle_checkin** module that integrates with the existing **vehicle_manager** module. The module manages driver check-ins/check-outs for vehicle assignments.

---

## Business Logic

### Core Workflow
1. **Check-In**: Assign an available vehicle to a driver
   - Driver selects from available vehicles (status='available')
   - System records check-in date/time
   - Vehicle status changes from 'available' to 'reserved'
   - Creates a check-in record linking driver → vehicle

2. **Check-Out**: Return vehicle and mark as available
   - Driver checks out from their assigned vehicle
   - System records check-out date/time
   - Vehicle status changes from 'reserved' to 'available'
   - Check-in record is marked as completed

### Key Relationships
```
vehicle.checkin (New Module)
    ↓ Many2one
vehicle.vehicle (Existing Module - vehicle_manager)
    
vehicle.checkin
    ↓ Many2one
res.partner (Driver - Standard Odoo Model)
```

---

## Module Structure

### Directory Layout
```
addons/vehicle_checkin/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── vehicle_checkin.py
├── views/
│   ├── vehicle_checkin_views.xml
│   └── menus.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── checkin_data.xml (optional demo data)
├── wizard/
│   ├── __init__.py
│   ├── checkin_wizard.py
│   └── checkout_wizard.py
├── static/
│   └── description/
│       ├── icon.png
│       └── index.html
└── README.md
```

---

## Step-by-Step Implementation

### 1. Module Manifest (`__manifest__.py`)

```python
{
    'name': 'Vehicle Check-In/Check-Out',
    'version': '18.0.1.0.0',
    'category': 'Fleet Management',
    'summary': 'Manage driver check-ins and check-outs for vehicles',
    'description': """
Vehicle Check-In/Check-Out Management
=====================================
* Check-in drivers with available vehicles
* Track vehicle usage periods
* Automatic vehicle status management
* Check-out process with return confirmation
* Integration with Vehicle Manager module
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'vehicle_manager',  # CRITICAL: Dependency on vehicle_manager
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/vehicle_checkin_views.xml',
        'views/menus.xml',
        'wizard/checkin_wizard_views.xml',
        'wizard/checkout_wizard_views.xml',
    ],
    'demo': [
        'data/checkin_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
```

**Key Points:**
- `depends`: Must include 'vehicle_manager' to access vehicle.vehicle model
- `application`: True makes it appear as main app in Odoo Apps
- Version format: `{odoo_version}.{major}.{minor}.{patch}`

---

### 2. Main Model (`models/vehicle_checkin.py`)

```python
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
    
    vehicle_brand = fields.Char(
        related='vehicle_id.brand',
        string='Brand',
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
```

**Key Implementation Notes:**
- Uses `_inherit = ['mail.thread', 'mail.activity.mixin']` for chatter functionality
- Implements proper constraints to prevent data inconsistencies
- Overrides `create()` and `write()` to manage vehicle status automatically
- Related fields (`vehicle_license_plate`, etc.) for easy access without joins
- Smart buttons ready (action_view_checkins, action_view_vehicle)

---

### 3. Check-In Wizard (`wizard/checkin_wizard.py`)

```python
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
    
    checkin_mileage = fields.Integer(
        string='Current Mileage',
        help="Vehicle mileage at check-in"
    )
    
    notes = fields.Text(string='Notes')
    
    def action_confirm_checkin(self):
        """Create check-in record and update vehicle status"""
        self.ensure_one()
        
        # Create check-in record
        checkin = self.env['vehicle.checkin'].create({
            'driver_id': self.driver_id.id,
            'vehicle_id': self.vehicle_id.id,
            'checkin_date': self.checkin_date,
            'checkin_mileage': self.checkin_mileage,
            'notes': self.notes,
            'state': 'checked_in',
        })
        
        # Show success notification
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
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'vehicle.checkin',
                    'res_id': checkin.id,
                    'view_mode': 'form',
                    'target': 'current',
                }
            }
        }
```

---

### 4. Check-Out Wizard (`wizard/checkout_wizard.py`)

```python
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
```

---

### 5. Views (`views/vehicle_checkin_views.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Check-In Form View -->
    <record id="view_vehicle_checkin_form" model="ir.ui.view">
        <field name="name">vehicle.checkin.form</field>
        <field name="model">vehicle.checkin</field>
        <field name="arch" type="xml">
            <form string="Vehicle Check-In">
                <header>
                    <button name="action_checkout" string="Check-Out" type="object" 
                            class="oe_highlight" invisible="state != 'checked_in'"/>
                    <button name="action_cancel" string="Cancel" type="object" 
                            confirm="Are you sure you want to cancel this check-in?" 
                            invisible="state != 'checked_in'"/>
                    <field name="state" widget="statusbar" statusbar_visible="checked_in,checked_out"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="action_view_vehicle" type="object" class="oe_stat_button" icon="fa-car">
                            <span>View Vehicle</span>
                        </button>
                    </div>
                    
                    <div class="oe_title">
                        <h1>
                            <field name="display_name" readonly="1"/>
                        </h1>
                    </div>
                    
                    <group>
                        <group string="Driver Information">
                            <field name="driver_id" options="{'no_create': True}"/>
                        </group>
                        <group string="Vehicle Information">
                            <field name="vehicle_id" options="{'no_create': True}"/>
                            <field name="vehicle_license_plate"/>
                            <field name="vehicle_brand"/>
                            <field name="vehicle_model"/>
                        </group>
                    </group>
                    
                    <group>
                        <group string="Check-In Details">
                            <field name="checkin_date"/>
                            <field name="checkin_mileage"/>
                        </group>
                        <group string="Check-Out Details">
                            <field name="checkout_date"/>
                            <field name="checkout_mileage"/>
                        </group>
                    </group>
                    
                    <group string="Duration" invisible="state != 'checked_out'">
                        <field name="duration_hours"/>
                        <field name="duration_days"/>
                        <field name="distance_traveled"/>
                    </group>
                    
                    <notebook>
                        <page string="Notes">
                            <field name="notes" placeholder="Enter any notes or observations..."/>
                        </page>
                    </notebook>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>
    
    <!-- Check-In List View -->
    <record id="view_vehicle_checkin_tree" model="ir.ui.view">
        <field name="name">vehicle.checkin.tree</field>
        <field name="model">vehicle.checkin</field>
        <field name="arch" type="xml">
            <list string="Vehicle Check-Ins" 
                  decoration-success="state=='checked_out'" 
                  decoration-info="state=='checked_in'"
                  decoration-muted="state=='cancelled'">
                <field name="checkin_date"/>
                <field name="driver_id"/>
                <field name="vehicle_license_plate"/>
                <field name="vehicle_brand"/>
                <field name="vehicle_model"/>
                <field name="checkout_date"/>
                <field name="duration_days" optional="hide"/>
                <field name="state" widget="badge" 
                       decoration-success="state=='checked_out'" 
                       decoration-info="state=='checked_in'"
                       decoration-danger="state=='cancelled'"/>
            </list>
        </field>
    </record>
    
    <!-- Check-In Kanban View -->
    <record id="view_vehicle_checkin_kanban" model="ir.ui.view">
        <field name="name">vehicle.checkin.kanban</field>
        <field name="model">vehicle.checkin</field>
        <field name="arch" type="xml">
            <kanban class="o_kanban_mobile">
                <field name="driver_id"/>
                <field name="vehicle_license_plate"/>
                <field name="checkin_date"/>
                <field name="state"/>
                <templates>
                    <t t-name="kanban-box">
                        <div class="oe_kanban_global_click">
                            <div class="o_kanban_record_top">
                                <div class="o_kanban_record_headings">
                                    <strong class="o_kanban_record_title">
                                        <field name="driver_id"/>
                                    </strong>
                                </div>
                                <span class="badge" t-att-class="record.state.raw_value == 'checked_in' ? 'badge-info' : 'badge-success'">
                                    <field name="state"/>
                                </span>
                            </div>
                            <div class="o_kanban_record_body">
                                <div>🚗 <field name="vehicle_license_plate"/></div>
                                <div>📅 <field name="checkin_date"/></div>
                            </div>
                        </div>
                    </t>
                </templates>
            </kanban>
        </field>
    </record>
    
    <!-- Check-In Search View -->
    <record id="view_vehicle_checkin_search" model="ir.ui.view">
        <field name="name">vehicle.checkin.search</field>
        <field name="model">vehicle.checkin</field>
        <field name="arch" type="xml">
            <search string="Search Check-Ins">
                <field name="driver_id"/>
                <field name="vehicle_id"/>
                <field name="vehicle_license_plate"/>
                <separator/>
                <filter string="Checked In" name="filter_checked_in" domain="[('state', '=', 'checked_in')]"/>
                <filter string="Checked Out" name="filter_checked_out" domain="[('state', '=', 'checked_out')]"/>
                <filter string="Cancelled" name="filter_cancelled" domain="[('state', '=', 'cancelled')]"/>
                <separator/>
                <filter string="This Month" name="filter_this_month" 
                        domain="[('checkin_date', '>=', (context_today() - relativedelta(months=1)).strftime('%Y-%m-%d'))]"/>
                <group expand="0" string="Group By">
                    <filter string="Driver" name="group_driver" context="{'group_by': 'driver_id'}"/>
                    <filter string="Vehicle" name="group_vehicle" context="{'group_by': 'vehicle_id'}"/>
                    <filter string="Status" name="group_state" context="{'group_by': 'state'}"/>
                    <filter string="Check-In Date" name="group_checkin_date" context="{'group_by': 'checkin_date:month'}"/>
                </group>
            </search>
        </field>
    </record>
    
    <!-- Action -->
    <record id="action_vehicle_checkin" model="ir.actions.act_window">
        <field name="name">Check-Ins</field>
        <field name="type">ir.actions.act_window</field>
        <field name="res_model">vehicle.checkin</field>
        <field name="view_mode">list,kanban,form</field>
        <field name="context">{'search_default_filter_checked_in': 1}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                No check-ins found!
            </p>
            <p>
                Click "New Check-In" to assign a vehicle to a driver.
            </p>
        </field>
    </record>
</odoo>
```

---

### 6. Wizard Views (`wizard/checkin_wizard_views.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Check-In Wizard Form -->
    <record id="view_vehicle_checkin_wizard_form" model="ir.ui.view">
        <field name="name">vehicle.checkin.wizard.form</field>
        <field name="model">vehicle.checkin.wizard</field>
        <field name="arch" type="xml">
            <form string="New Check-In">
                <sheet>
                    <group>
                        <group>
                            <field name="driver_id" options="{'no_create': True}"/>
                            <field name="vehicle_id" options="{'no_create': True}"/>
                        </group>
                        <group>
                            <field name="checkin_date"/>
                            <field name="checkin_mileage"/>
                        </group>
                    </group>
                    <group string="Notes">
                        <field name="notes" nolabel="1" placeholder="Enter any notes..."/>
                    </group>
                </sheet>
                <footer>
                    <button string="Confirm Check-In" name="action_confirm_checkin" type="object" class="btn-primary"/>
                    <button string="Cancel" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>
    
    <!-- Check-In Wizard Action -->
    <record id="action_vehicle_checkin_wizard" model="ir.actions.act_window">
        <field name="name">New Check-In</field>
        <field name="res_model">vehicle.checkin.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
        <field name="view_id" ref="view_vehicle_checkin_wizard_form"/>
    </record>
</odoo>
```

**Checkout wizard similar structure** - see wizard/checkout_wizard_views.xml

---

### 7. Security (`security/ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_vehicle_checkin_user,vehicle.checkin.user,model_vehicle_checkin,base.group_user,1,1,1,1
access_vehicle_checkin_wizard_user,vehicle.checkin.wizard.user,model_vehicle_checkin_wizard,base.group_user,1,1,1,1
access_vehicle_checkout_wizard_user,vehicle.checkout.wizard.user,model_vehicle_checkout_wizard,base.group_user,1,1,1,1
```

**Access Rights Explanation:**
- `model_id:id`: References the model (auto-generated by Odoo)
- `group_id:id`: User group (base.group_user = internal users)
- Permissions: read, write, create, unlink (1=allowed, 0=denied)

---

### 8. Menus (`views/menus.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Main Menu -->
    <menuitem id="menu_vehicle_checkin_root" 
              name="Vehicle Check-In" 
              sequence="51"
              web_icon="vehicle_checkin,static/description/icon.png"/>
    
    <!-- Check-Ins Menu -->
    <menuitem id="menu_vehicle_checkin_list" 
              name="Check-Ins" 
              parent="menu_vehicle_checkin_root"
              action="action_vehicle_checkin" 
              sequence="10"/>
    
    <!-- New Check-In Menu -->
    <menuitem id="menu_vehicle_checkin_new" 
              name="New Check-In" 
              parent="menu_vehicle_checkin_root"
              action="action_vehicle_checkin_wizard" 
              sequence="20"/>
</odoo>
```

---

## Integration with vehicle_manager Module

### Key Integration Points

1. **Model Extension**
```python
class VehicleVehicle(models.Model):
    _inherit = 'vehicle.vehicle'
    
    # Add fields to existing vehicle model
    checkin_ids = fields.One2many('vehicle.checkin', 'vehicle_id', 'Check-Ins')
    current_driver_id = fields.Many2one('res.partner', 'Current Driver', compute='...')
```

2. **Status Synchronization**
- Check-in creates → vehicle.status = 'reserved'
- Check-out completes → vehicle.status = 'available'

3. **Smart Buttons on Vehicle Form**
Add to `vehicle_manager/views/vehicle_views.xml`:
```xml
<button name="action_view_checkins" type="object" class="oe_stat_button" icon="fa-history">
    <field name="checkin_count" widget="statinfo" string="Check-Ins"/>
</button>
```

4. **Domain Filters**
Check-in wizard shows only: `domain=[('status', '=', 'available')]`

---

## Testing Strategy

### Manual Testing Checklist
1. ✅ Create check-in with available vehicle
2. ✅ Verify vehicle status changes to 'reserved'
3. ✅ Try to check-in same vehicle twice (should fail)
4. ✅ Check-out vehicle
5. ✅ Verify vehicle status returns to 'available'
6. ✅ Verify duration calculations
7. ✅ Test mileage constraints (checkout > checkin)
8. ✅ Test date constraints (checkout after checkin)
9. ✅ View check-in history from vehicle form

### Unit Test Example (`tests/test_vehicle_checkin.py`)

```python
from odoo.tests import common
from odoo.exceptions import ValidationError

class TestVehicleCheckin(common.TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.vehicle = self.env['vehicle.vehicle'].create({
            'brand': 'Toyota',
            'model': 'Camry',
            'license_plate': 'TEST-123',
            'status': 'available',
        })
        self.driver = self.env['res.partner'].create({
            'name': 'Test Driver',
            'is_company': False,
        })
    
    def test_checkin_changes_vehicle_status(self):
        """Test that check-in changes vehicle status to reserved"""
        checkin = self.env['vehicle.checkin'].create({
            'driver_id': self.driver.id,
            'vehicle_id': self.vehicle.id,
        })
        self.assertEqual(self.vehicle.status, 'reserved')
    
    def test_checkout_makes_vehicle_available(self):
        """Test that check-out makes vehicle available"""
        checkin = self.env['vehicle.checkin'].create({
            'driver_id': self.driver.id,
            'vehicle_id': self.vehicle.id,
        })
        checkin.write({
            'checkout_date': fields.Datetime.now(),
            'state': 'checked_out',
        })
        self.assertEqual(self.vehicle.status, 'available')
    
    def test_cannot_checkin_reserved_vehicle(self):
        """Test that you cannot check-in a reserved vehicle"""
        # First check-in
        checkin1 = self.env['vehicle.checkin'].create({
            'driver_id': self.driver.id,
            'vehicle_id': self.vehicle.id,
        })
        
        # Second check-in should fail
        driver2 = self.env['res.partner'].create({'name': 'Driver 2'})
        with self.assertRaises(ValidationError):
            self.env['vehicle.checkin'].create({
                'driver_id': driver2.id,
                'vehicle_id': self.vehicle.id,
            })
```

---

## Installation & Setup

### 1. Create Module Structure
```bash
cd /home/aleixo/odoo/addons
./odoo-bin scaffold vehicle_checkin ./
```

### 2. Copy Code Files
Create all Python and XML files as documented above.

### 3. Update Manifest Dependencies
Ensure `__manifest__.py` includes `'vehicle_manager'` in depends list.

### 4. Install Module
```bash
./odoo-bin -d DATABASE_NAME -i vehicle_checkin
```

### 5. Update Module (after changes)
```bash
./odoo-bin -d DATABASE_NAME -u vehicle_checkin
```

---

## Advanced Features (Future Enhancements)

1. **Automatic Notifications**
   - Email driver when vehicle is assigned
   - Reminder notifications for overdue returns

2. **Reports**
   - Vehicle usage reports
   - Driver performance reports
   - Monthly check-in/out summaries

3. **Mobile App Integration**
   - QR code scanning for quick check-in
   - Mobile-friendly views

4. **GPS Tracking**
   - Track vehicle location during check-in
   - Geofencing alerts

5. **Damage Documentation**
   - Photo uploads at check-in/out
   - Damage comparison reports

6. **Billing Integration**
   - Automatic billing based on usage
   - Integration with accounting modules

---

## Common Pitfalls & Solutions

### Problem: Module doesn't appear after installation
**Solution**: Clear browser cache and restart Odoo server with `--dev=all`

### Problem: "Model not found" error
**Solution**: Check `depends` in manifest includes 'vehicle_manager'

### Problem: Access denied errors
**Solution**: Check `ir.model.access.csv` has correct permissions

### Problem: Vehicle status not updating
**Solution**: Check `create()` and `write()` methods are overridden correctly

### Problem: Constraint violations
**Solution**: Ensure `@api.constrains` decorators are on correct fields

---

## Best Practices

1. **Always use transactions** - Odoo handles this automatically
2. **Use computed fields** for calculated data (duration, distance)
3. **Add tracking=True** to important fields for audit trail
4. **Use related fields** to avoid unnecessary database joins
5. **Implement proper constraints** to ensure data integrity
6. **Add helpful error messages** in ValidationError exceptions
7. **Use chatter** for activity logging
8. **Create wizards** for complex user interactions
9. **Test thoroughly** before production deployment

---

## File Checklist

- [ ] `__init__.py` (root and models/, wizard/)
- [ ] `__manifest__.py`
- [ ] `models/vehicle_checkin.py`
- [ ] `wizard/checkin_wizard.py`
- [ ] `wizard/checkout_wizard.py`
- [ ] `views/vehicle_checkin_views.xml`
- [ ] `wizard/checkin_wizard_views.xml`
- [ ] `wizard/checkout_wizard_views.xml`
- [ ] `views/menus.xml`
- [ ] `security/ir.model.access.csv`
- [ ] `static/description/icon.png`
- [ ] `README.md`

---

## Quick Reference Commands

```bash
# Install module
./odoo-bin -d DATABASE_NAME -i vehicle_checkin

# Update module
./odoo-bin -d DATABASE_NAME -u vehicle_checkin

# Development mode (auto-reload)
./odoo-bin --dev=all -d DATABASE_NAME

# Run tests
./odoo-bin --test-enable --stop-after-init -d test_db -i vehicle_checkin

# Upgrade specific module with logging
./odoo-bin -d DATABASE_NAME -u vehicle_checkin --log-level=debug
```

---

This guide provides complete instructions for building a production-ready vehicle check-in/check-out module integrated with the vehicle_manager module. Follow the structure and patterns documented here for consistent, maintainable Odoo development.
