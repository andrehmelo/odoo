# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import base64
import io
import csv
import logging
from datetime import datetime

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
    
    # Column mapping
    col_make = fields.Char(string='Make/Brand Column', default='Marca')
    col_model = fields.Char(string='Model Column', default='Modelo')
    col_year = fields.Char(string='Year Column', default='year')
    col_vin = fields.Char(string='VIN Column', default='VIN')
    col_license_plate = fields.Char(string='License Plate Column', default='Matrícula')
    col_color = fields.Char(string='Color Column', default='color')
    col_body_type = fields.Char(string='Body Type Column', default='body_type')
    col_doors = fields.Char(string='Doors Column', default='doors')
    col_seats = fields.Char(string='Seats Column', default='seats')
    col_engine_size = fields.Char(string='Engine Size Column', default='engine_size')
    col_engine_type = fields.Char(string='Fuel Type Column', default='engine_type')
    col_transmission = fields.Char(string='Transmission Column', default='transmission')
    col_drivetrain = fields.Char(string='Drivetrain Column', default='drivetrain')
    col_mileage = fields.Char(string='Mileage Column', default='mileage')
    col_mileage_unit = fields.Char(string='Mileage Unit Column', default='mileage_unit')
    col_condition = fields.Char(string='Condition Column', default='condition')
    col_purchase_price = fields.Char(string='Purchase Price Column', default='Valor Evmob')
    col_current_value = fields.Char(string='Current Value Column', default='current_value')
    col_status = fields.Char(string='Status Column', default='status')
    col_purchase_date = fields.Char(string='Purchase Date Column', default='Data Compra/Aluguer')
    col_location = fields.Char(string='Location Column', default='location')
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
        
        # Parse CSV
        csv_file = io.StringIO(content_str)
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
            'make': self.col_make,
            'model': self.col_model,
            'year': self.col_year,
            'vin': self.col_vin,
            'license_plate': self.col_license_plate,
            'color': self.col_color,
            'body_type': self.col_body_type,
            'doors': self.col_doors,
            'seats': self.col_seats,
            'engine_size': self.col_engine_size,
            'engine_type': self.col_engine_type,
            'transmission': self.col_transmission,
            'drivetrain': self.col_drivetrain,
            'mileage': self.col_mileage,
            'mileage_unit': self.col_mileage_unit,
            'condition': self.col_condition,
            'purchase_price': self.col_purchase_price,
            'current_value': self.col_current_value,
            'status': self.col_status,
            'purchase_date': self.col_purchase_date,
            'location': self.col_location,
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
            if field_name in ['year', 'doors', 'seats']:
                return int(float(value))  # Handle decimal strings like "2020.0"
            
            elif field_name in ['engine_size', 'mileage', 'purchase_price', 'current_value']:
                # Skip empty values
                if not value or value.strip() == '':
                    return False
                # Remove currency symbols and commas
                cleaned = str(value).replace(',', '').replace('$', '').replace('€', '').replace('£', '').replace(' ', '').strip()
                if cleaned:
                    return float(cleaned)
                return False
            
            elif field_name == 'purchase_date':
                # Skip empty or invalid values
                if not value or value.strip() == '':
                    return False
                    
                # Try to parse date in various formats (Portuguese format first)
                for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y']:
                    try:
                        return datetime.strptime(value.strip(), fmt).date()
                    except ValueError:
                        continue
                _logger.warning(f"Could not parse date '{value}' in row {row_num}")
                return False
            
            elif field_name in ['body_type', 'engine_type', 'transmission', 'drivetrain', 'condition', 'status', 'mileage_unit']:
                # Map common variations to valid selection values
                value_lower = value.lower()
                
                if field_name == 'body_type':
                    mapping = {
                        'sedan': 'sedan', 'car': 'sedan',
                        'hatchback': 'hatchback', 'hatch': 'hatchback',
                        'suv': 'suv', 'sport utility': 'suv',
                        'truck': 'truck', 'pickup': 'truck',
                        'coupe': 'coupe', 'coupé': 'coupe',
                        'convertible': 'convertible', 'cabriolet': 'convertible',
                        'wagon': 'wagon', 'estate': 'wagon', 'station wagon': 'wagon',
                        'van': 'van', 'minivan': 'van',
                        'motorcycle': 'motorcycle', 'bike': 'motorcycle',
                    }
                elif field_name == 'engine_type':
                    mapping = {
                        'gasoline': 'gasoline', 'gas': 'gasoline', 'petrol': 'gasoline',
                        'diesel': 'diesel', 'diesel fuel': 'diesel',
                        'hybrid': 'hybrid', 'hybrid electric': 'hybrid',
                        'electric': 'electric', 'ev': 'electric', 'battery': 'electric',
                    }
                elif field_name == 'transmission':
                    mapping = {
                        'manual': 'manual', 'stick': 'manual', 'mt': 'manual',
                        'automatic': 'automatic', 'auto': 'automatic', 'at': 'automatic',
                        'cvt': 'cvt', 'continuously variable': 'cvt',
                        'semi-automatic': 'semi_automatic', 'semi automatic': 'semi_automatic',
                    }
                elif field_name == 'condition':
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
                
                return mapping.get(value_lower, value)
            
            else:
                return value
                
        except (ValueError, TypeError) as e:
            _logger.warning(f"Error converting value '{value}' for field '{field_name}' in row {row_num}: {e}")
            return False
    
    def action_import_vehicles(self):
        """Perform the vehicle import"""
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
        
        # Import vehicles
        import_log = []
        created_count = 0
        updated_count = 0
        error_count = 0
        
        Vehicle = self.env['vehicle.vehicle']
        
        for row_num, row in enumerate(data_rows, start=(2 if self.has_header else 1)):
            try:
                # Skip empty rows
                if not any(cell.strip() if isinstance(cell, str) else cell for cell in row):
                    continue
                    
                # Extract values based on column mapping
                vehicle_vals = {}
                
                for field, col_index in column_indices.items():
                    if col_index < len(row):
                        raw_value = row[col_index]
                        if raw_value and str(raw_value).strip():  # Skip empty values
                            converted_value = self._convert_value(field, str(raw_value).strip(), row_num)
                            if converted_value is not False:  # Allow empty string but not False
                                vehicle_vals[field] = converted_value
                
                # Set all imported vehicles to available status
                vehicle_vals['status'] = 'available'
                
                # Ensure year is set (required field)
                if not vehicle_vals.get('year'):
                    model_name = vehicle_vals.get('model', '')
                    # Try to extract year from model string
                    import re
                    year_match = re.search(r'\b(19|20)\d{2}\b', model_name)
                    if year_match:
                        vehicle_vals['year'] = int(year_match.group())
                    else:
                        # Set a reasonable default year
                        vehicle_vals['year'] = 2020
                
                # Validate required fields
                if not vehicle_vals.get('make') or not vehicle_vals.get('model'):
                    import_log.append(f"Row {row_num}: Skipped - Missing make or model")
                    error_count += 1
                    continue
                
                # Use separate transaction for each vehicle to avoid rollback issues
                with self.env.cr.savepoint():
                    # Handle existing vehicle update
                    existing_vehicle = False
                    if self.update_existing and vehicle_vals.get('vin'):
                        existing_vehicle = Vehicle.search([('vin', '=', vehicle_vals['vin'])], limit=1)
                    
                    if existing_vehicle:
                        existing_vehicle.write(vehicle_vals)
                        import_log.append(f"Row {row_num}: Updated vehicle {existing_vehicle.name}")
                        updated_count += 1
                    else:
                        new_vehicle = Vehicle.create(vehicle_vals)
                        import_log.append(f"Row {row_num}: Created vehicle {new_vehicle.name}")
                        created_count += 1
                    
            except Exception as e:
                import_log.append(f"Row {row_num}: Error - {str(e)}")
                error_count += 1
                _logger.error(f"Error importing row {row_num}: {e}")
                # Continue with next row even if this one failed
        
        # Prepare summary
        summary = f"Import completed:\n"
        summary += f"- Created: {created_count} vehicles\n"
        summary += f"- Updated: {updated_count} vehicles\n"  
        summary += f"- Errors: {error_count} rows\n\n"
        summary += "Details:\n" + "\n".join(import_log)
        
        # Update import log using sudo to avoid permission issues
        try:
            self.sudo().write({'import_log': summary})
        except Exception as e:
            _logger.warning(f"Could not update import log: {e}")
        
        # Show results
        if error_count == 0:
            message = f"Import successful! Created {created_count} and updated {updated_count} vehicles."
            message_type = 'success'
        else:
            message = f"Import completed with {error_count} errors. Created {created_count} and updated {updated_count} vehicles."
            message_type = 'warning'
        
        # Return action to reload wizard with results
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Results',
            'res_model': 'vehicle.import.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {
                'default_import_log': summary,
            }
        }
    
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