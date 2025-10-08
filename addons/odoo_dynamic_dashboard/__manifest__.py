{
    # Basic Module Information
    'name': "fleet_analytics",
    'version': '1.0',
    'category': 'fleet',

    # Description and Attribution
    'summary': 'The purpose of this module is to create analytics dashboard for fleet management data.',
    'description': 'The purpose of this module is to create analytics dashboard for fleet management data.',
    'author': 'Prisma Solutions',
    'company': 'Prisma Solutions',
    'maintainer': 'Prisma Solutions',
    'website': "https://prismaconsulting.odoo.com/",

    # Dependencies and Data Files
    'depends': ['web'],
    'data': [
        'security/ir.model.access.csv',
        'data/dashboard_theme_data.xml',
        'views/dashboard_views.xml',
        'views/dynamic_block_views.xml',
        'views/dashboard_menu_views.xml',
        'views/dashboard_theme_views.xml',
        'wizard/dashboard_mail_views.xml',
    ],

    # Web Assets
    
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js',
            'odoo_dynamic_dashboard/static/src/css/**/*.css',
            'odoo_dynamic_dashboard/static/src/scss/**/*.scss',
            'odoo_dynamic_dashboard/static/src/js/**/*.js',
            'odoo_dynamic_dashboard/static/src/xml/**/*.xml',
            'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css',
            'odoo_dynamic_dashboard/static/src/js/interact_min.js'
        ],
    },

    # Module Configuration
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}



