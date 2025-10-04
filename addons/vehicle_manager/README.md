# Vehicle Manager Module

A comprehensive vehicle inventory management system for Odoo that allows you to track, manage, and analyze your vehicle fleet with Excel/CSV import capabilities.

## Features

### Vehicle Management
- Complete vehicle inventory with detailed specifications
- Track vehicle status (Available, Reserved, Sold, Under Maintenance)
- Vehicle condition monitoring (Excellent, Good, Fair, Poor)
- Financial tracking (purchase price, selling price, profit margins)
- Comprehensive vehicle details (make, model, year, color, etc.)

### Import Capabilities
- Import vehicles from Excel (.xlsx, .xls) files
- Import vehicles from CSV files
- Flexible column mapping during import
- Data validation and error handling
- Batch import processing

### User Interface
- **Kanban View**: Visual cards grouped by status
- **Tree View**: Comprehensive list with sorting and filtering
- **Form View**: Detailed vehicle information with status workflow
- **Advanced Search**: Filter by make, model, year, status, condition
- **Dashboard**: Quick access to available and sold vehicles

### Technical Features
- Data validation and constraints
- Automatic profit calculation
- Status workflow management
- Comprehensive access rights and security
- Demo data included for testing

## Installation

1. Copy the module to your Odoo addons directory
2. Update the module list: Go to Apps → Update Apps List
3. Search for "Vehicle Manager" and install
4. The module will be available in the main menu

## Usage

### Adding Vehicles Manually
1. Go to Vehicle Management → All Vehicles
2. Click "Create" to add a new vehicle
3. Fill in the vehicle details and save

### Importing from Excel/CSV
1. Go to Vehicle Management → Import Vehicles
2. Select your Excel or CSV file
3. Map the columns to the corresponding fields
4. Click "Import" to process the data

### Managing Vehicle Status
- Use the status buttons in the form view to change vehicle status
- Track the complete lifecycle from purchase to sale
- Monitor vehicles under maintenance or reserved

## File Format for Import

Your Excel/CSV file can include these columns:
- Name, Make, Model, Year, Color
- VIN, License Plate, Engine Size, Mileage
- Fuel Type, Transmission, Condition, Status
- Purchase Price, Selling Price, Purchase Date
- Doors, Seats, Description, Internal Notes

## Support

For issues or feature requests, please contact your system administrator.

## Version

Version 1.0.0 - Compatible with Odoo 18.0