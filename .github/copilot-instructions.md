# Odoo Development Copilot Instructions

## Architecture Overview

Odoo is a modular ERP framework where functionality is organized into **addons**. Each addon follows a strict structure:
- `__manifest__.py`: Addon metadata, dependencies, and asset declarations
- `models/`: Python models inheriting from `odoo.models.Model`  
- `views/`: XML view definitions (forms, lists, kanban, etc.)
- `security/`: Access control files (`ir.model.access.csv`)
- `data/`: Data XML files for default records
- `static/src/`: Frontend assets (JS, CSS, XML templates)

## Key Development Patterns

### Model Definition
```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model Description' 
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Common mixins
    _rec_name = 'name'  # Display name field
    _order = 'name desc'
    
    name = fields.Char(required=True, tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')])
    
    @api.depends('field1', 'field2')
    def _compute_total(self):
        for record in self:
            record.total = record.field1 + record.field2
```

### View Structure (XML)
```xml
<odoo>
    <record id="view_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>  
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm" string="Confirm" type="object"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <field name="name"/>
                </sheet>
            </form>
        </field>
    </record>
</odoo>
```

### JavaScript (Owl Framework)
Use `/** @odoo-module **/` at top of JS files. Import using `@odoo/` prefix:
```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";
```

## Critical Development Commands

### Server Management
```bash
./odoo-bin --dev=all --database=DATABASE_NAME  # Development mode with auto-reload
./odoo-bin -d DATABASE_NAME -i ADDON_NAME      # Install addon
./odoo-bin -d DATABASE_NAME -u ADDON_NAME      # Update addon
```

### Scaffolding
```bash
./odoo-bin scaffold addon_name ./addons/        # Generate addon skeleton
```

### Testing
```bash
./odoo-bin --test-enable --stop-after-init -d test_db -i addon_name
```

## Manifest File Structure
```python
{
    'name': 'Addon Name',
    'version': '18.0.1.0.0',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'addon_name/static/src/**/*.js',
            'addon_name/static/src/**/*.scss',
        ],
    },
}
```

## Database & ORM Conventions

- Models use dot notation: `vehicle.vehicle`, `sale.order`
- Field naming: `snake_case`, avoid reserved words
- Relations: `partner_id` (Many2one), `line_ids` (One2many)
- Computed fields require `@api.depends()` decorator
- Use `self.env['model.name']` for cross-model access

## Security & Access Control

Every model needs `security/ir.model.access.csv`:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model,access_my_model,model_my_model,base.group_user,1,1,1,1
```

## Web Framework (Frontend)

- Use Owl components for complex UI
- QWeb templates for server-side rendering
- Assets bundled via `assets` in manifest
- Controllers handle HTTP routes: `@http.route('/my/route', auth='user')`

## Configuration

- `odoo.conf`: Database connection, logging, addons path
- Environment variables: `ODOO_RC` for config file path
- Development: Use `--dev=all` for auto-reload and enhanced debugging

## Common Integration Points

- Mail system: Inherit `mail.thread` for chatter/activity features  
- Website: Use `website` module dependency for portal features
- Reporting: QWeb reports in `report/` directory
- API: External integrations via `/web/dataset/call_kw` endpoint

## Version & Compatibility

- This is Odoo 18.0 (Python 3.10-3.13 supported)
- Addons version format: `{odoo_version}.{major}.{minor}.{patch}`
- Migration scripts in `migrations/` directory when upgrading versions