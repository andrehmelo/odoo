# -*- coding: utf-8 -*-
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
    'author': 'Prisma Consulting',
    'website': 'https://prismaconsulting.odoo.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'vehicle_manager',
        'drivers_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/vehicle_checkin_dashboard.xml',
        'views/vehicle_checkin_views.xml',
        'views/vehicle_vehicle_views.xml',
        'views/drivers_management_views.xml',
        'wizard/checkin_wizard_views.xml',
        'wizard/direct_checkout_wizard_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'data/checkin_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vehicle_checkin/static/src/js/dashboard.js',
            'vehicle_checkin/static/src/xml/dashboard.xml',
            'vehicle_checkin/static/src/js/checkin_list_controller.js',
            'vehicle_checkin/static/src/xml/checkin_list_buttons.xml',
            'vehicle_checkin/static/src/js/checkin_kanban_controller.js',
            'vehicle_checkin/static/src/xml/checkin_kanban_buttons.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
