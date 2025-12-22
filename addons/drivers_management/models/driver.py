from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Driver(models.Model):
    _name = 'drivers.management'
    _description = 'Driver Management'
    _order = 'priority desc, name'

    # Core Fields
    name = fields.Char(string='Name', required=True, index='trigram')
    status = fields.Selection([
        ('lead', 'Lead'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status', default='lead', required=True, index=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority', default='1')
    
    # Computed field to check if driver is a lead
    is_lead = fields.Boolean(compute='_compute_is_lead', store=True)
    
    # Computed field to check if has platform info
    has_platform_info = fields.Boolean(compute='_compute_has_platform_info', store=True)

    # Personal Information (required for active/inactive)
    email = fields.Char(string='Personal Email', index='trigram')
    nr_telemovel = fields.Char(string='Phone Number')
    nif = fields.Char(string='NIF')
    iban = fields.Char(string='IBAN')

    # Uber Platform
    email_uber = fields.Char(string='Uber Email')
    nr_telemovel_uber = fields.Char(string='Uber Phone')
    nome_uber = fields.Char(string='Uber Name')
    id_uber = fields.Char(string='Uber ID')

    # Bolt Platform
    email_bolt = fields.Char(string='Bolt Email')
    nr_telemovel_bolt = fields.Char(string='Bolt Phone')
    nome_bolt = fields.Char(string='Bolt Name')
    id_bolt = fields.Char(string='Bolt ID')

    # Vehicle Assignment
    vehicle_id = fields.Many2one('vehicle.vehicle', string='Assigned Vehicle', ondelete='set null')

    # Dates
    date_assigned = fields.Datetime('Assignment Date', readonly=True, copy=False)
    days_since_assignment = fields.Float('Days Since Assignment', compute='_compute_days_since_assignment', store=True)

    # System Fields
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible')
    tag_ids = fields.Many2many('drivers.tag', string='Tags')
    color = fields.Integer('Color Index', default=0)
    description = fields.Html('Notes')

    _sql_constraints = [
        ('unique_id_uber', 'unique(id_uber)', 'Uber ID must be unique!'),
        ('unique_id_bolt', 'unique(id_bolt)', 'Bolt ID must be unique!'),
        ('unique_nif', 'unique(nif)', 'NIF must be unique!'),
    ]
    
    @api.depends('status')
    def _compute_is_lead(self):
        for driver in self:
            driver.is_lead = driver.status == 'lead'
    
    @api.depends('id_uber', 'id_bolt')
    def _compute_has_platform_info(self):
        """Check if driver has at least one platform (Uber or Bolt) configured"""
        for driver in self:
            has_uber = bool(driver.id_uber)
            has_bolt = bool(driver.id_bolt)
            driver.has_platform_info = has_uber or has_bolt

    def _validate_lead_requirements(self, vals, record=None):
        """Lead needs: name + (phone OR email)"""
        email = vals.get('email') if 'email' in vals else (record.email if record else False)
        phone = vals.get('nr_telemovel') if 'nr_telemovel' in vals else (record.nr_telemovel if record else False)
        if not email and not phone:
            raise ValidationError(
                _("A lead must have at least a Phone Number or Email address.")
            )
    
    def _validate_inactive_requirements(self, vals, record=None):
        """Inactive (registered driver) needs: Uber OR Bolt platform info"""
        # Skip validation if called from wizard with context
        if self.env.context.get('skip_platform_validation'):
            return
            
        # Check Uber
        id_uber = vals.get('id_uber') if 'id_uber' in vals else (record.id_uber if record else False)
        # Check Bolt  
        id_bolt = vals.get('id_bolt') if 'id_bolt' in vals else (record.id_bolt if record else False)
        
        if not id_uber and not id_bolt:
            raise ValidationError(
                _("To register a driver you must fill at least one platform: Uber ID or Bolt ID.")
            )
    
    def _validate_active_requirements(self, vals, record=None):
        """Active driver needs: vehicle assigned via check-in"""
        # Active status is managed through check-in system
        # Skip direct validation - check-in handles vehicle assignment
        pass

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            status = vals.get('status') or self.env.context.get('default_status', 'lead')
            # For leads, only validate lead requirements
            if status == 'lead':
                self._validate_lead_requirements(vals)
            elif status == 'inactive':
                self._validate_lead_requirements(vals)
                self._validate_inactive_requirements(vals)
            elif status == 'active':
                # Active status should only be set through check-in
                self._validate_lead_requirements(vals)
                self._validate_inactive_requirements(vals)
        return super().create(vals_list)

    def write(self, vals):
        for driver in self:
            status = vals.get('status', driver.status)
            # Validate based on target status
            if status == 'lead':
                self._validate_lead_requirements(vals, driver)
            elif status == 'inactive':
                self._validate_lead_requirements(vals, driver)
                self._validate_inactive_requirements(vals, driver)
            elif status == 'active':
                # Active status is managed through check-in system
                self._validate_lead_requirements(vals, driver)
                self._validate_inactive_requirements(vals, driver)
        
        return super().write(vals)
    
    def unlink(self):
        """Prevent deletion of active drivers"""
        for driver in self:
            if driver.status == 'active':
                raise ValidationError(
                    _("Cannot delete active driver '%s'. Please deactivate (checkout) first.") % driver.name
                )
        return super().unlink()

    @api.depends('date_assigned')
    def _compute_days_since_assignment(self):
        for driver in self:
            if driver.date_assigned:
                delta = fields.Datetime.now() - driver.date_assigned
                driver.days_since_assignment = delta.days
            else:
                driver.days_since_assignment = None

    def action_save_lead(self):
        """Save the current lead - triggers form save and stays on record"""
        # The record is saved automatically when button is clicked
        # Return action to reload the form view of the saved record
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'drivers.management',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_register_wizard(self):
        """Open the Register Driver wizard to collect platform info"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Register Driver'),
            'res_model': 'drivers.register.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_driver_id': self.id,
            }
        }

    def action_activate_driver(self):
        """Activate driver by opening check-in wizard"""
        self.ensure_one()
        
        if self.status != 'inactive':
            raise ValidationError(_("Only inactive (registered) drivers can be activated."))
        
        # Open the check-in wizard from vehicle_checkin module
        return {
            'type': 'ir.actions.act_window',
            'name': _('Check-In Vehicle'),
            'res_model': 'vehicle.checkin.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_driver_id': self.id,
            }
        }

    def action_deactivate_driver(self):
        """Deactivate driver by opening checkout wizard for active check-in"""
        self.ensure_one()
        
        if self.status != 'active':
            raise ValidationError(_("Only active drivers can be deactivated."))
        
        # Find the active check-in for this driver
        active_checkin = self.env['vehicle.checkin'].search([
            ('driver_id', '=', self.id),
            ('state', '=', 'checked_in'),
            ('checkout_date', '=', False)
        ], limit=1)
        
        if not active_checkin:
            raise ValidationError(_("No active check-in found for this driver. Cannot deactivate."))
        
        # Open the checkout wizard
        return active_checkin.action_checkout()
    
    def action_convert_to_lead(self):
        """Convert back to Lead status - clears platform info"""
        self.ensure_one()
        
        # Cannot convert active driver - must checkout first
        if self.status == 'active':
            raise ValidationError(
                _("Cannot convert an active driver to lead. Please deactivate (checkout) first.")
            )
        
        self.write({
            'status': 'lead',
            'vehicle_id': False,
        })
    
    def action_delete_driver(self):
        """Delete the driver record"""
        self.ensure_one()
        
        # Cannot delete active drivers
        if self.status == 'active':
            raise ValidationError(
                _("Cannot delete an active driver. Please deactivate (checkout) first.")
            )
        
        driver_name = self.name
        self.unlink()
        
        # Return to the drivers list view
        return {
            'type': 'ir.actions.act_window',
            'name': _('Drivers'),
            'res_model': 'drivers.management',
            'view_mode': 'kanban,list,form',
            'target': 'current',
        }