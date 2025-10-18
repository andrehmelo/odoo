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
        'mail',
        'vehicle_manager',  # CRITICAL: Dependency on vehicle_manager
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/vehicle_checkin_views.xml',
        'wizard/checkin_wizard_views.xml',
        'wizard/checkout_wizard_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'data/checkin_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
