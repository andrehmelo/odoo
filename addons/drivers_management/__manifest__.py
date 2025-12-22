{
    'name': 'Drivers Management',
    'version': '1.0',
    'category': 'Human Resources/Drivers',
    'sequence': 80,
    'author': 'Prisma Solutions',
    'summary': 'Manage drivers for various platforms',
    'description': """
        This module provides functionality to manage drivers, including:
        * Driver profiles and documentation
        * Status management (Lead, Active, Inactive)
        * Integration with Uber and Bolt platforms
        * Vehicle assignment and tracking
        * Banking and legal information
    """,
    'depends': [
        'base',
        'vehicle_manager',
    ],
    'data': [
        'security/drivers_security.xml',
        'security/ir.model.access.csv',
        'views/drivers_views.xml',
        'views/drivers_menus.xml',
        'data/drivers_data.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}