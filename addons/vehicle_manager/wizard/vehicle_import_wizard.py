# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import base64
import io
import csv
import json
import logging
from datetime import datetime, date

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

_logger = logging.getLogger(__name__)


class VehicleImportWizard(models.TransientModel):
    _name = 'vehicle.import.wizard'
    _description = 'Vehicle Import Wizard'
    
    file_data = fields.Binary(
        string='Upload File',
        required=True,
        help="Upload Excel (.xlsx) or CSV file containing vehicle data"
    )
    file_name = fields.Char(string='File Name')
    file_type = fields.Selection([
        ('csv', 'CSV File'),
        ('excel', 'Excel File (.xlsx)'),
    ], string='File Type', compute='_compute_file_type', store=True)
    
    # Import options
    has_header = fields.Boolean(
        string='File has header row',
        default=True,
        help="Check if first row contains column headers"
    )
    delimiter = fields.Selection([
        (',', 'Comma (,)'),
        (';', 'Semicolon (;)'),
        ('\t', 'Tab'),
        ('|', 'Pipe (|)'),
    ], string='CSV Delimiter', default=',')
    
    update_existing = fields.Boolean(
        string='Update Existing Records',
        default=False,
        help="Update existing vehicles (matched by VIN) instead of creating duplicates"
    )
    
    # Wizard state
    state = fields.Selection([
        ('upload', 'Upload File'),
        ('preview', 'Preview Results'),
    ], default='upload', string='State')
    
    # Store parsed vehicle data as JSON
    vehicle_data = fields.Text(string='Vehicle Data', readonly=True)
    
    # Column mapping - Updated to match current vehicle form
    # Basic Information
    col_make = fields.Char(string='Make/Brand Column', default='Marca')
    col_model = fields.Char(string='Model Column', default='Modelo')
    col_vin = fields.Char(string='VIN Column', default='VIN')
    col_license_plate = fields.Char(string='License Plate Column', default='Matrícula')
    col_color = fields.Char(string='Color Column', default='color')
    col_year = fields.Char(string='Year Column', default='year')
    
    # Driver Fees
    col_weekly_rent = fields.Char(string='Weekly Rent Column', default='weekly_rent')
    col_entry_deposit = fields.Char(string='Entry Deposit Column', default='entry_deposit')
    col_reserve_fee = fields.Char(string='Reserve Fee Column', default='reserve_fee')
    col_reserve_fee_max = fields.Char(string='Reserve Fee Max Column', default='reserve_fee_max')
    
    # Financial Information
    col_purchase_price = fields.Char(string='Purchase Price Column', default='Valor Evmob')
    col_current_value = fields.Char(string='Current Value Column', default='current_value')
    col_purchase_date = fields.Char(string='Purchase Date Column', default='Data Compra/Aluguer')
    
    # Car Details
    col_via_verde_card = fields.Char(string='Via Verde Card Column', default='via_verde_card')
    col_gas_card = fields.Char(string='Gas Card Column', default='gas_card')
    col_fire_extinguisher = fields.Char(string='Fire Extinguisher ID Column', default='fire_extinguisher')
    col_insurance_date = fields.Char(string='Insurance Expiry Column', default='insurance_date')
    col_ipo_date = fields.Char(string='IPO Expiry Column', default='ipo_date')
    col_condition = fields.Char(string='Condition Column', default='condition')
    
    # Mileage & Usage
    col_mileage = fields.Char(string='Mileage Column', default='mileage')
    col_mileage_unit = fields.Char(string='Mileage Unit Column', default='mileage_unit')
    col_location = fields.Char(string='Current Location Column', default='location')
    
    # Contact Information
    col_owner_id = fields.Char(string='Owner/Contact Column', default='owner')
    
    # Additional (optional)
    col_status = fields.Char(string='Status Column', default='status')
    col_features = fields.Char(string='Features Column', default='features')
    col_notes = fields.Char(string='Notes Column', default='notes')
    
    # Import results
    import_log = fields.Text(string='Import Log', readonly=True)
    
    @api.depends('file_name')
    def _compute_file_type(self):
        """Auto-detect file type based on extension"""
        for wizard in self:
            if wizard.file_name:
                if wizard.file_name.lower().endswith('.xlsx'):
                    wizard.file_type = 'excel'
                elif wizard.file_name.lower().endswith('.csv'):
                    wizard.file_type = 'csv'
                else:
                    wizard.file_type = 'csv'  # default to CSV
            else:
                wizard.file_type = 'csv'
    
    def _parse_csv_data(self, file_content):
        """Parse CSV file content"""
        try:
            # Detect encoding
            content_str = file_content.decode('utf-8-sig')  # Handle BOM
        except UnicodeDecodeError:
            try:
                content_str = file_content.decode('latin-1')
            except UnicodeDecodeError:
                content_str = file_content.decode('utf-8', errors='ignore')
        
        # Parse CSV with proper newline handling
        csv_file = io.StringIO(content_str, newline='')
        reader = csv.reader(csv_file, delimiter=self.delimiter)
        rows = list(reader)
        
        return rows
    
    def _parse_excel_data(self, file_content):
        """Parse Excel file content"""
        if not OPENPYXL_AVAILABLE:
            raise UserError(_("openpyxl library is required for Excel imports. Please install it with: pip install openpyxl"))
        
        workbook = openpyxl.load_workbook(io.BytesIO(file_content))
        worksheet = workbook.active
        
        rows = []
        for row in worksheet.iter_rows(values_only=True):
            # Convert None values to empty strings and handle other data types
            row_data = []
            for cell in row:
                if cell is None:
                    row_data.append('')
                elif isinstance(cell, datetime):
                    row_data.append(cell.strftime('%Y-%m-%d'))
                else:
                    row_data.append(str(cell))
            rows.append(row_data)
        
        return rows
    
    def _get_column_mapping(self):
        """Get column mapping configuration"""
        return {
            # Basic Information
            'make': self.col_make,
            'model': self.col_model,
            'vin': self.col_vin,
            'license_plate': self.col_license_plate,
            'color': self.col_color,
            'year': self.col_year,
            # Driver Fees
            'weekly_rent': self.col_weekly_rent,
            'entry_deposit': self.col_entry_deposit,
            'reserve_fee': self.col_reserve_fee,
            'reserve_fee_max': self.col_reserve_fee_max,
            # Financial Information
            'purchase_price': self.col_purchase_price,
            'current_value': self.col_current_value,
            'purchase_date': self.col_purchase_date,
            # Car Details
            'via_verde_card': self.col_via_verde_card,
            'gas_card': self.col_gas_card,
            'fire_extinguisher': self.col_fire_extinguisher,
            'insurance_date': self.col_insurance_date,
            'ipo_date': self.col_ipo_date,
            'condition': self.col_condition,
            # Mileage & Usage
            'mileage': self.col_mileage,
            'mileage_unit': self.col_mileage_unit,
            'location': self.col_location,
            # Contact Information
            'owner_id': self.col_owner_id,
            # Additional
            'status': self.col_status,
            'features': self.col_features,
            'notes': self.col_notes,
        }
    
    def _create_column_index_map(self, headers):
        """Create mapping from column names to indices"""
        mapping = self._get_column_mapping()
        column_indices = {}
        
        # Normalize headers (lowercase, strip spaces)
        normalized_headers = [h.lower().strip() for h in headers]
        
        for field, column_name in mapping.items():
            if not column_name:
                continue
                
            # Try exact match first
            if column_name.lower() in normalized_headers:
                column_indices[field] = normalized_headers.index(column_name.lower())
            else:
                # Try partial match
                for i, header in enumerate(normalized_headers):
                    if column_name.lower() in header or header in column_name.lower():
                        column_indices[field] = i
                        break
        
        return column_indices
    
    def _convert_value(self, field_name, value, row_num):
        """Convert string value to appropriate type for field"""
        if not value or str(value).strip() == '':
            return False
        
        value = str(value).strip()
        
        try:
            if field_name in ['year']:
                # Convert year to date (use January 1st of that year)
                year_int = int(float(value))
                from datetime import date
                return date(year_int, 1, 1)
            
            elif field_name in ['mileage', 'purchase_price', 'current_value', 'weekly_rent', 'entry_deposit', 'reserve_fee', 'reserve_fee_max']:
                # Skip empty values
                if not value or value.strip() == '':
                    return False
                # Remove currency symbols and commas
                cleaned = str(value).replace(',', '').replace('$', '').replace('€', '').replace('£', '').replace(' ', '').strip()
                if cleaned:
                    return float(cleaned)
                return False
            
            elif field_name in ['via_verde_card', 'gas_card', 'fire_extinguisher']:
                # These are string IDs (can contain letters/numbers), max 30 chars
                return str(value).strip()[:30]
            
            elif field_name in ['purchase_date', 'insurance_date', 'ipo_date']:
                # Skip empty or invalid values
                if not value or value.strip() == '':
                    return False
                
                value = value.strip()
                
                # Check if it's just a year (e.g., "2020")
                if value.isdigit() and len(value) == 4:
                    year_int = int(value)
                    return date(year_int, 1, 1)  # Convert to January 1st of that year
                    
                # Try to parse date in various formats (Portuguese format first)
                for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y']:
                    try:
                        return datetime.strptime(value, fmt).date()
                    except ValueError:
                        continue
                _logger.warning(f"Could not parse date '{value}' in row {row_num}")
                return False
            
            elif field_name in ['condition', 'status', 'mileage_unit']:
                # Map common variations to valid selection values
                value_lower = value.lower()
                
                if field_name == 'condition':
                    mapping = {
                        'new': 'new', 'brand new': 'new',
                        'excellent': 'excellent', 'like new': 'excellent',
                        'good': 'good', 'very good': 'good',
                        'fair': 'fair', 'average': 'fair',
                        'poor': 'poor', 'below average': 'poor',
                        'damaged': 'damaged', 'needs repair': 'damaged',
                    }
                elif field_name == 'status':
                    mapping = {
                        'available': 'available', 'in stock': 'available', 'for sale': 'available',
                        'reserved': 'reserved', 'hold': 'reserved', 'pending': 'reserved',
                        'sold': 'sold', 'delivered': 'sold',
                        'maintenance': 'maintenance', 'service': 'maintenance', 'repair': 'maintenance',
                        'damaged': 'damaged', 'accident': 'damaged',
                        'retired': 'retired', 'scrapped': 'retired',
                    }
                elif field_name == 'mileage_unit':
                    mapping = {
                        'km': 'km', 'kilometers': 'km', 'kilometres': 'km',
                        'miles': 'miles', 'mi': 'miles', 'mile': 'miles',
                    }
                else:
                    mapping = {}
                
                return mapping.get(value_lower, value)
            
            else:
                return value
                
        except (ValueError, TypeError) as e:
            _logger.warning(f"Error converting value '{value}' for field '{field_name}' in row {row_num}: {e}")
            return False
    
    def action_import_vehicles(self):
        """Parse and preview the vehicle import (doesn't commit yet)"""
        if not self.file_data:
            raise UserError(_("Please upload a file first."))
        
        # Decode file data
        file_content = base64.b64decode(self.file_data)
        
        # Parse file based on type
        if self.file_type == 'excel':
            rows = self._parse_excel_data(file_content)
        else:
            rows = self._parse_csv_data(file_content)
        
        if not rows:
            raise UserError(_("The file appears to be empty or could not be parsed."))
        
        # Get headers and data rows
        if self.has_header:
            headers = rows[0]
            data_rows = rows[1:]
        else:
            # Generate generic headers
            headers = [f'Column_{i+1}' for i in range(len(rows[0]))]
            data_rows = rows
        
        # Create column mapping
        column_indices = self._create_column_index_map(headers)
        
        # Parse and validate data WITHOUT committing to database
        vehicles_to_import = []
        import_log = []
        error_count = 0
        will_create_count = 0
        will_update_count = 0
        
        # Track VINs and license plates seen in this import to detect duplicates within CSV
        seen_vins = {}  # {vin: row_num}
        seen_license_plates = {}  # {license_plate: row_num}
        
        Vehicle = self.env['vehicle.vehicle']
        
        for row_num, row in enumerate(data_rows, start=(2 if self.has_header else 1)):
            try:
                # Skip empty rows
                if not any(cell.strip() if isinstance(cell, str) else cell for cell in row):
                    continue
                    
                # Extract values based on column mapping
                vehicle_vals = {}
                
                for field, col_index in column_indices.items():
                    # Skip status field - all imports should be 'available'
                    if field == 'status':
                        continue
                        
                    if col_index < len(row):
                        raw_value = row[col_index]
                        if raw_value and str(raw_value).strip():  # Skip empty values
                            converted_value = self._convert_value(field, str(raw_value).strip(), row_num)
                            if converted_value is not False:  # Allow empty string but not False
                                vehicle_vals[field] = converted_value
                
                # Always set all imported vehicles to available status
                vehicle_vals['status'] = 'available'
                
                # Ensure year is set (required field)
                if not vehicle_vals.get('year'):
                    model_name = vehicle_vals.get('model', '')
                    # Try to extract year from model string
                    import re
                    from datetime import date
                    year_match = re.search(r'\b(19|20)\d{2}\b', model_name)
                    if year_match:
                        year_int = int(year_match.group())
                        vehicle_vals['year'] = date(year_int, 1, 1)
                    else:
                        # Set a reasonable default year
                        vehicle_vals['year'] = date(2020, 1, 1)
                
                # Validate required fields
                if not vehicle_vals.get('make') or not vehicle_vals.get('model'):
                    import_log.append(f"Row {row_num}: ❌ Skipped - Missing make or model")
                    error_count += 1
                    continue
                
                # Check for duplicate VIN within this CSV
                if vehicle_vals.get('vin'):
                    vin_upper = vehicle_vals['vin'].upper()
                    vehicle_vals['vin'] = vin_upper  # Normalize to uppercase
                    
                    if vin_upper in seen_vins:
                        import_log.append(f"Row {row_num}: ❌ Duplicate VIN '{vin_upper}' (first seen in row {seen_vins[vin_upper]})")
                        error_count += 1
                        continue
                    seen_vins[vin_upper] = row_num
                    
                    # Check if VIN already exists in database
                    existing_by_vin = Vehicle.search([('vin', '=', vin_upper)], limit=1)
                    if existing_by_vin and not self.update_existing:
                        import_log.append(f"Row {row_num}: ❌ VIN '{vin_upper}' already exists in database (vehicle: {existing_by_vin.name})")
                        error_count += 1
                        continue
                
                # Check for duplicate license plate within this CSV
                if vehicle_vals.get('license_plate'):
                    plate_upper = vehicle_vals['license_plate'].upper()
                    vehicle_vals['license_plate'] = plate_upper  # Normalize to uppercase
                    
                    if plate_upper in seen_license_plates:
                        import_log.append(f"Row {row_num}: ❌ Duplicate license plate '{plate_upper}' (first seen in row {seen_license_plates[plate_upper]})")
                        error_count += 1
                        continue
                    seen_license_plates[plate_upper] = row_num
                    
                    # Check if license plate already exists in database
                    existing_by_plate = Vehicle.search([('license_plate', '=', plate_upper)], limit=1)
                    if existing_by_plate and not self.update_existing:
                        import_log.append(f"Row {row_num}: ❌ License plate '{plate_upper}' already exists in database (vehicle: {existing_by_plate.name})")
                        error_count += 1
                        continue
                
                # Check if will update or create (without committing)
                existing_vehicle = False
                if self.update_existing and vehicle_vals.get('vin'):
                    existing_vehicle = Vehicle.search([('vin', '=', vehicle_vals['vin'])], limit=1)
                
                # Store for later processing - convert date objects to strings for JSON
                vehicle_vals_serializable = {}
                for key, val in vehicle_vals.items():
                    if isinstance(val, date):
                        vehicle_vals_serializable[key] = val.isoformat()
                    else:
                        vehicle_vals_serializable[key] = val
                
                vehicle_info = {
                    'row': row_num,
                    'vals': vehicle_vals_serializable,
                    'is_update': bool(existing_vehicle),
                    'existing_id': existing_vehicle.id if existing_vehicle else False,
                }
                vehicles_to_import.append(vehicle_info)
                
                # Generate display name for preview - use the original date object for display
                year_display = vehicle_vals.get('year', '').year if vehicle_vals.get('year') else ''
                display_name = f"{year_display} {vehicle_vals.get('make', '')} {vehicle_vals.get('model', '')}".strip()
                
                if existing_vehicle:
                    import_log.append(f"Row {row_num}: ✏️ Will UPDATE vehicle: {display_name}")
                    will_update_count += 1
                else:
                    import_log.append(f"Row {row_num}: ✅ Will CREATE vehicle: {display_name}")
                    will_create_count += 1
                    
            except Exception as e:
                import_log.append(f"Row {row_num}: Error - {str(e)}")
                error_count += 1
                _logger.error(f"Error importing row {row_num}: {e}")
                # Continue with next row even if this one failed
        
        # Prepare preview summary
        summary = f"Import Preview:\n"
        summary += f"- Will CREATE: {will_create_count} vehicles\n"
        summary += f"- Will UPDATE: {will_update_count} vehicles\n"  
        summary += f"- Errors/Skipped: {error_count} rows\n\n"
        summary += "Details:\n" + "\n".join(import_log)
        
        # Store vehicle data as JSON for later processing
        self.write({
            'vehicle_data': json.dumps(vehicles_to_import),
            'import_log': summary,
            'state': 'preview',
        })
        
        # Return action to reload wizard in preview state
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Preview - Review Before Saving',
            'res_model': 'vehicle.import.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
    
    def action_save_import(self):
        """Actually commit the vehicles to database"""
        if not self.vehicle_data:
            raise UserError(_("No vehicle data to import."))
        
        vehicles_to_import = json.loads(self.vehicle_data)
        
        created_count = 0
        updated_count = 0
        error_count = 0
        error_details = []
        Vehicle = self.env['vehicle.vehicle']
        
        for vehicle_info in vehicles_to_import:
            try:
                vehicle_vals = vehicle_info['vals'].copy()
                
                # Convert all date strings back to date objects
                date_fields = ['year', 'purchase_date', 'insurance_date', 'ipo_date']
                for field in date_fields:
                    if vehicle_vals.get(field) and isinstance(vehicle_vals[field], str):
                        year_parts = vehicle_vals[field].split('-')
                        vehicle_vals[field] = date(int(year_parts[0]), int(year_parts[1]), int(year_parts[2]))
                
                if vehicle_info['is_update']:
                    existing_vehicle = Vehicle.browse(vehicle_info['existing_id'])
                    existing_vehicle.write(vehicle_vals)
                    updated_count += 1
                else:
                    Vehicle.create(vehicle_vals)
                    created_count += 1
                    
            except Exception as e:
                error_count += 1
                error_msg = f"Row {vehicle_info['row']}: {str(e)}"
                error_details.append(error_msg)
                _logger.error(f"Error saving vehicle from row {vehicle_info['row']}: {e}")
        
        # Build success message
        message = f"Created {created_count}"
        if updated_count > 0:
            message += f" and updated {updated_count}"
        message += f" vehicle{'s' if (created_count + updated_count) != 1 else ''}."
        
        if error_count > 0:
            message += f" {error_count} error{'s' if error_count != 1 else ''} occurred."
        
        # Get the vehicle list action to reload it
        action = self.env.ref('vehicle_manager.action_vehicle_vehicle').read()[0]
        
        # Return notification and then open vehicle list
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Import Complete'),
                'message': message,
                'type': 'success' if error_count == 0 else 'warning',
                'sticky': False,
                'next': action,
            }
        }
    
    def action_discard_import(self):
        """Discard the import and close wizard"""
        return {'type': 'ir.actions.act_window_close'}
    
    def action_download_template(self):
        """Download CSV template for vehicle import"""
        headers = [
            'Matrícula', 'Marca', 'Modelo', 'VIN', 'Data Compra/Aluguer', 'Valor Evmob'
        ]
        
        # Create sample data matching your Portuguese format
        sample_data = [
            ['14-ZG-80', 'Fiat', 'Panda 1.2 69cv GPL Bi-Fuel Easy', 'ZFA31200003D36601', '2/12/2020', '185'],
            ['15-ZG-02', 'Fiat', 'Panda 1.2 69cv GPL Bi-Fuel Easy', 'ZFA31200003D37658', '2/5/2020', '185'],
            ['ABC-123', 'Toyota', 'Camry 2.0L', '1HGBH41JXMN109186', '15/06/2021', '25000']
        ]
        
        # Generate CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(sample_data)
        csv_content = output.getvalue()
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'vehicle_import_template.csv',
            'type': 'binary',
            'datas': base64.b64encode(csv_content.encode('utf-8')),
            'mimetype': 'text/csv',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }