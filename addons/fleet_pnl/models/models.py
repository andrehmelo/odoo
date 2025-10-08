from odoo import api, models, fields, _
# Double check if we can have all classes defined here or if we need to split them in different files


class FleetDriver(models.Model):
    _name = 'fleet.driver'
    _description = 'Fleet Driver'

    ref = fields.Char(string='Ref')
    name = fields.Char(string='Name')

    weekly_revenue = fields.Float(string='Weekly Revenue')
    weekly_gasoline_costs = fields.Float(string='Weekly Gasoline Costs')
    weekly_wifi_card_costs = fields.Float(string='Weekly WiFi Card Costs')
    assigned_vehicle_id = fields.Many2one('fleet.vehicle', string='Assigned Vehicle')
    weekly_vehicle_depreciation = fields.Float(string='Weekly Vehicle Depreciation')
    weekly_other_costs = fields.Float(string='Weekly Other Costs')
    vehicle_photo = fields.Image(string='Vehicle Photo')
    
