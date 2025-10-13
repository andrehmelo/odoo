# -*- coding: utf-8 -*-
{
    "name": "Cards & Tolls",
    "summary": "Track Via Verde tolls and fuel card transactions for the fleet.",
    "version": "1.0",
    "depends": ["base", "fleet", "mail"],
    "author": "Your Company",
    "category": "Operations/Fleet",
    "license": "LGPL-3",
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "views/via_verde_views.xml",
        "views/gas_card_views.xml",
        "views/via_verde_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "via_verde/static/src/js/mobility_cards_dashboard.js",
            "via_verde/static/src/xml/mobility_cards_dashboard.xml",
            "via_verde/static/src/scss/mobility_cards_dashboard.scss",
        ],
    },
}
