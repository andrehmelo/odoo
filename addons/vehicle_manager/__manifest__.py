# -*- coding: utf-8 -*-
{
    'name': 'Vehicle Manager',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Manage vehicle inventory with Excel/CSV import functionality',
    'description': """
Vehicle Management System
=========================
Complete vehicle inventory management solution with:

* Vehicle registration and tracking
* Detailed vehicle information (make, model, year, VIN, etc.)
* Excel/CSV import wizard for bulk vehicle uploads
* Advanced search and filtering
* Vehicle status management (Available, Sold, Reserved, etc.)
* Professional dashboard and reporting views

Features:
---------
* Import vehicles from Excel (.xlsx) or CSV files
* Comprehensive vehicle data management
* User-friendly interface with advanced search
* Vehicle status tracking and management
* Data validation and error handling during import
    """,
    'author': 'Prisma Consulting',
    'website': 'https://prismaconsulting.odoo.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'base_import',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/vehicle_data.xml',
        'views/vehicle_views.xml',
        'views/vehicle_import_wizard_views.xml',
        'views/vehicle_delete_wizard_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vehicle_manager/static/src/css/vehicle_manager.css',
            'vehicle_manager/static/src/js/vehicle_delete_button.js',
            'vehicle_manager/static/src/js/vehicle_kanban.js',
            'vehicle_manager/static/src/js/vehicle_appsbar_integration.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}