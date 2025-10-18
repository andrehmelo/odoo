# Vehicle Check-In/Check-Out Module

## Overview
This module provides driver check-in and check-out functionality for vehicle management, integrating seamlessly with the Vehicle Manager module.

## Features
- **Driver Check-In**: Assign available vehicles to drivers with automatic status updates
- **Vehicle Check-Out**: Return vehicles with mileage tracking and condition reporting
- **Integration**: Seamlessly integrates with the vehicle_manager module
- **Tracking**: Complete check-in/check-out history with chatter support
- **Validation**: Prevents double-booking and ensures data integrity
- **Reports**: Duration tracking, mileage calculation, and usage statistics

## Business Logic

### Check-In Workflow
1. Driver selects from available vehicles (status='available')
2. System records check-in date/time and mileage
3. Vehicle status automatically changes to 'reserved'
4. Check-in record is created with driver assignment

### Check-Out Workflow
1. Driver initiates check-out from assigned vehicle
2. System records check-out date/time, mileage, fuel level, and condition
3. Vehicle status automatically changes back to 'available'
4. Duration and distance traveled are calculated automatically

## Installation

1. Ensure `vehicle_manager` module is installed
2. Install this module:
   ```bash
   ./odoo-bin -d DATABASE_NAME -i vehicle_checkin
   ```

## Usage

### Creating a Check-In
1. Navigate to **Vehicle Check-In > New Check-In**
2. Select driver and available vehicle
3. Enter mileage and any notes
4. Click **Confirm Check-In**

### Processing a Check-Out
1. Open the check-in record
2. Click **Check-Out** button
3. Enter checkout mileage, fuel level, and vehicle condition
4. Add any damage description if needed
5. Click **Confirm Check-Out**

## Dependencies
- `base`
- `mail`
- `vehicle_manager`

## Technical Details

### Models
- `vehicle.checkin`: Main check-in/check-out records
- `vehicle.vehicle`: Extended with check-in history and current driver
- `vehicle.checkin.wizard`: Wizard for new check-ins
- `vehicle.checkout.wizard`: Wizard for check-outs

### Views
- Form, List, Kanban, and Search views for check-ins
- Wizard dialogs for check-in/check-out processes
- Integration with vehicle form view

## Version
18.0.1.0.0

## Author
Prisma Consulting

## License
LGPL-3
