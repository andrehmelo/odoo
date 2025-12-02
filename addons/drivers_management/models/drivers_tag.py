from odoo import fields, models

class DriverTag(models.Model):
    _name = 'drivers.tag'
    _description = 'Driver Tags'
    
    name = fields.Char('Tag Name', required=True, translate=True)
    color = fields.Integer('Color Index', default=0)
    active = fields.Boolean(default=True)
