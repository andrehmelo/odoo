# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RegisterDriverWizard(models.TransientModel):
    _name = 'drivers.register.wizard'
    _description = 'Register Driver Wizard'
    
    driver_id = fields.Many2one(
        'drivers.management',
        string='Driver',
        required=True,
        readonly=True
    )
    
    # Display driver info (readonly)
    driver_name = fields.Char(
        related='driver_id.name',
        string='Driver Name',
        readonly=True
    )
    driver_email = fields.Char(
        related='driver_id.email',
        string='Email',
        readonly=True
    )
    driver_phone = fields.Char(
        related='driver_id.nr_telemovel',
        string='Phone',
        readonly=True
    )
    
    # Legal & Banking (validated in action method)
    nif = fields.Char(string='NIF')
    iban = fields.Char(string='IBAN')
    
    # Platform selection
    platform = fields.Selection([
        ('uber', 'Uber'),
        ('bolt', 'Bolt'),
        ('both', 'Both Platforms'),
    ], string='Platform', required=True, default='uber')
    
    # Uber fields
    id_uber = fields.Char(string='Uber ID')
    nome_uber = fields.Char(string='Uber Name')
    email_uber = fields.Char(string='Uber Email')
    nr_telemovel_uber = fields.Char(string='Uber Phone')
    
    # Bolt fields
    id_bolt = fields.Char(string='Bolt ID')
    nome_bolt = fields.Char(string='Bolt Name')
    email_bolt = fields.Char(string='Bolt Email')
    nr_telemovel_bolt = fields.Char(string='Bolt Phone')
    
    @api.onchange('platform')
    def _onchange_platform(self):
        """Clear non-selected platform fields"""
        if self.platform == 'uber':
            self.id_bolt = False
            self.nome_bolt = False
            self.email_bolt = False
            self.nr_telemovel_bolt = False
        elif self.platform == 'bolt':
            self.id_uber = False
            self.nome_uber = False
            self.email_uber = False
            self.nr_telemovel_uber = False
    
    def action_register_driver(self):
        """Complete registration and set driver to Inactive"""
        self.ensure_one()
        
        # Validate NIF and IBAN are filled
        missing_required = []
        if not self.nif:
            missing_required.append('NIF')
        if not self.iban:
            missing_required.append('IBAN')
        if missing_required:
            raise ValidationError(_("Please fill required fields: %s") % ', '.join(missing_required))
        
        # Validate Uber platform - all fields required
        if self.platform in ('uber', 'both'):
            missing_uber = []
            if not self.id_uber:
                missing_uber.append('Uber ID')
            if not self.nome_uber:
                missing_uber.append('Uber Name')
            if not self.email_uber:
                missing_uber.append('Uber Email')
            if not self.nr_telemovel_uber:
                missing_uber.append('Uber Phone')
            if missing_uber:
                raise ValidationError(_("Please fill all Uber fields: %s") % ', '.join(missing_uber))
        
        # Validate Bolt platform - all fields required
        if self.platform in ('bolt', 'both'):
            missing_bolt = []
            if not self.id_bolt:
                missing_bolt.append('Bolt ID')
            if not self.nome_bolt:
                missing_bolt.append('Bolt Name')
            if not self.email_bolt:
                missing_bolt.append('Bolt Email')
            if not self.nr_telemovel_bolt:
                missing_bolt.append('Bolt Phone')
            if missing_bolt:
                raise ValidationError(_("Please fill all Bolt fields: %s") % ', '.join(missing_bolt))
        
        # Prepare values to update driver
        vals = {
            'status': 'inactive',
            'nif': self.nif,
            'iban': self.iban,
        }
        
        # Add Uber info if filled
        if self.platform in ('uber', 'both'):
            vals.update({
                'id_uber': self.id_uber,
                'nome_uber': self.nome_uber,
                'email_uber': self.email_uber,
                'nr_telemovel_uber': self.nr_telemovel_uber,
            })
        
        # Add Bolt info if filled
        if self.platform in ('bolt', 'both'):
            vals.update({
                'id_bolt': self.id_bolt,
                'nome_bolt': self.nome_bolt,
                'email_bolt': self.email_bolt,
                'nr_telemovel_bolt': self.nr_telemovel_bolt,
            })
        
        # Update driver - bypass validation since we're setting platform info
        self.driver_id.with_context(skip_platform_validation=True).write(vals)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Driver "%s" has been registered successfully!', self.driver_id.name),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
