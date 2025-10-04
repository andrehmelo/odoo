# -*- coding: utf-8 -*-
{
    "name": "Via Verde Fleet Tolls",
    "summary": "Manage Via Verde toll transactions for fleet vehicles.",
    "version": "1.0",
    "depends": ["base", "fleet", "mail"],
    "author": "Your Company",
    "category": "Operations/Fleet",
    "license": "LGPL-3",
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "views/via_verde_menus.xml",
        "views/via_verde_views.xml",
    ],
    "assets": {},
}
