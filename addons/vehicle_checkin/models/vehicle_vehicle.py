# -*- coding: utf-8 -*-

from odoo import models, fields


class VehicleExtended(models.Model):
    _inherit = 'vehicle.vehicle'
    
    # Driver Check-In History Relationship
    checkin_ids = fields.One2many(
        'vehicle.checkin',
        'vehicle_id',
        string='Driver History',
        help="History of driver check-ins and check-outs for this vehicle"
    )
