# Hidden Default Odoo Actions

## Overview
We've disabled several default Odoo actions that don't make sense for the Vehicle Manager module.

## Disabled Actions

### 1. **Import Records** (`import="false"`)
- **Where**: List views (vehicles and intervention history)
- **Reason**: We have a custom import wizard specifically designed for vehicle imports
- **Impact**: "Import" option removed from Action menu gear icon

### 2. **Duplicate** (`duplicate="false"`)
- **Where**: All views (list, kanban) for both vehicles and intervention history
- **Reason**: Duplicating vehicles doesn't make sense - each vehicle should be unique
- **Impact**: "Duplicate" option removed from Action menu gear icon

### 3. **Archive/Unarchive** (`archivable="false"`)
- **Where**: Kanban views for vehicles and intervention history
- **Reason**: We use explicit delete actions and status management instead of archiving
- **Impact**: Archive/Unarchive options removed from group menu gear icon in kanban view

### 4. **Export Excel** (kept enabled: `export_xlsx="true"`)
- **Status**: ENABLED
- **Reason**: Users should be able to export data to Excel for reporting
- **Available in**: List views only

## Views Updated

### Vehicle Views (`vehicle_views.xml`)
1. **List View** (`view_vehicle_tree`):
   - `import="false"` - No import from list view
   - `export_xlsx="true"` - Allow Excel export
   - `duplicate="false"` - No duplicate option

2. **Kanban View** (`view_vehicle_kanban`):
   - `archivable="false"` - No archive/unarchive in groups
   - `import="false"` - No import option
   - `duplicate="false"` - No duplicate option

### Intervention History Views (`car_intervention_history_views.xml`)
1. **List View** (`view_car_intervention_history_tree`):
   - `import="false"` - No import option
   - `export_xlsx="true"` - Allow Excel export
   - `duplicate="false"` - No duplicate option

2. **Kanban View** (`view_car_intervention_history_kanban`):
   - `archivable="false"` - No archive/unarchive in groups
   - `import="false"` - No import option
   - `duplicate="false"` - No duplicate option

## Available Actions

Users will still see these options in the Action menu:
- ✅ **Export (Excel)** - For data reporting and backup
- ✅ **Delete** - Through custom delete actions in forms/kanban
- ✅ **Bulk Delete Operations** - Through custom wizard

## Technical Notes

### Why Keep `active` Field?
The `active` field remains in the vehicle model for potential future use, but the UI options for archive/unarchive are hidden. This maintains database flexibility while simplifying the user interface.

### Custom Import vs Default Import
We disabled the default import because:
1. Our custom import wizard validates VINs, license plates, and other vehicle-specific data
2. It provides preview before saving
3. It handles duplicate detection
4. It shows clear error messages for data issues

## User Impact

**Before**: Users saw confusing options like "Archive", "Duplicate", and "Import Records" that didn't make sense for vehicle management.

**After**: Users only see relevant actions:
- Export data to Excel
- Delete vehicles (when appropriate)
- Use custom import wizard for adding vehicles
- Use custom bulk delete operations for mass changes

This creates a cleaner, more intuitive interface focused on actual vehicle management workflows.
