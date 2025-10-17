# Year Display Enhancement

## Overview
Added a computed field `year_display` to show only the year number (e.g., "2020") instead of the full date format.

## Changes Made

### Model (`models/vehicle.py`)
```python
year_display = fields.Char(
    string='Year',
    compute='_compute_year_display',
    store=False,
    help="Display year only (computed from year field)"
)

@api.depends('year')
def _compute_year_display(self):
    """Display only the year from the date field"""
    for vehicle in self:
        if vehicle.year:
            vehicle.year_display = str(vehicle.year.year)
        else:
            vehicle.year_display = ''
```

### Form View (`views/vehicle_views.xml`)
- Added `year_display` field shown as readonly
- Kept `year` field for date picker input

## Result
- **In form view**: Users see "Year: 2020" (just the number)
- **When editing**: Date picker available to select year/month
- **In lists/kanban**: Can display year_display for cleaner look

## Technical Details
- `year` field stores the full date (YYYY-MM-DD)
- `year_display` extracts just the year portion (YYYY)
- Computed field is not stored in database (calculated on-the-fly)
- No performance impact as computation is simple

## Usage
Replace `<field name="year"/>` with `<field name="year_display"/>` in any view where you want to show only the year number.
