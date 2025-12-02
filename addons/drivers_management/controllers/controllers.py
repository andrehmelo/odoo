from odoo import http
from odoo.http import request

class DriversController(http.Controller):
    @http.route('/drivers', auth='user', type='http', website=True, methods=['GET'])
    def list_drivers(self, **kwargs):
        try:
            domain = []
            search_term = kwargs.get('search', '')
            if search_term:
                domain = [('name', 'ilike', search_term)]
            
            drivers = request.env['drivers.management'].search(domain)
            return request.render('drivers_management.drivers_list', {
                'drivers': drivers,
                'search_term': search_term,
            })
        except Exception as e:
            return request.render('drivers_management.error', {'error': str(e)})

    @http.route('/drivers/<model("drivers.management"):driver>', auth='user', type='http', website=True, methods=['GET'])
    def driver_detail(self, driver, **kwargs):
        if not driver.exists():
            return request.not_found()
        return request.render('drivers_management.driver_detail', {
            'driver': driver,
        })