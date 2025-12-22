# -*- coding: utf-8 -*-

from odoo import models, fields


class DriverExtended(models.Model):
    _inherit = 'drivers.management'
    
    # Check-In History Relationship
    checkin_ids = fields.One2many(
        'vehicle.checkin',
        'driver_id',
        string='Check-In History',
        help='History of vehicle check-ins for this driver'
    )
