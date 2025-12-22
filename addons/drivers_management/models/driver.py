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

    # Personal Information
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

    _status_required_fields = {
        'inactive': ['email', 'nr_telemovel', 'nif', 'iban'],
        'active': ['email', 'nr_telemovel', 'nif', 'iban', 'vehicle_id'],
    }

    def _validate_required_fields_for_status(self, vals, status, record=None):
        required_fields = self._status_required_fields.get(status)
        if not required_fields:
            return
        missing = []
        for field_name in required_fields:
            value = vals.get(field_name) if field_name in vals else (record[field_name] if record else False)
            if not value:
                missing.append(self._fields[field_name].string)
        if missing:
            raise ValidationError(
                _("To set a driver as %(status)s you must fill: %(fields)s",
                  status=status.capitalize(), fields=', '.join(missing))
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            status = vals.get('status') or self.env.context.get('default_status', 'lead')
            self._validate_required_fields_for_status(vals, status)
            if status == 'active' and not vals.get('date_assigned'):
                vals['date_assigned'] = fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        for driver in self:
            status = vals.get('status', driver.status)
            self._validate_required_fields_for_status(vals, status, driver)
        if 'status' in vals and vals['status'] == 'active':
            for driver in self:
                if driver.status != 'active' and not driver.date_assigned:
                    vals['date_assigned'] = fields.Datetime.now()
                    break
        return super().write(vals)

    @api.depends('date_assigned')
    def _compute_days_since_assignment(self):
        for driver in self:
            if driver.date_assigned:
                delta = fields.Datetime.now() - driver.date_assigned
                driver.days_since_assignment = delta.days
            else:
                driver.days_since_assignment = None

    def action_mark_active(self):
        """Mark driver as Active"""
        self.write({'status': 'active'})

    def action_mark_inactive(self):
        """Mark driver as Inactive"""
        self.write({'status': 'inactive'})