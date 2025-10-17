# -*- coding: utf-8 -*-
"""
Migration script to convert year from Integer to Date field
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Convert year integer values to date before field type change"""
    _logger.info("Starting migration: Converting year from Integer to Date")
    
    # Check if year column exists and is integer type
    cr.execute("""
        SELECT data_type 
        FROM information_schema.columns 
        WHERE table_name='vehicle_vehicle' AND column_name='year'
    """)
    result = cr.fetchone()
    
    if result and result[0] == 'integer':
        _logger.info("Found integer year column, converting to date...")
        
        # Create a temporary column for the date
        cr.execute("""
            ALTER TABLE vehicle_vehicle 
            ADD COLUMN IF NOT EXISTS year_temp date
        """)
        
        # Convert integer years to dates (January 1st of that year)
        # Handle NULL values and invalid years
        cr.execute("""
            UPDATE vehicle_vehicle 
            SET year_temp = CASE 
                WHEN year IS NOT NULL AND year >= 1900 AND year <= 2100 
                THEN make_date(year, 1, 1)
                ELSE NULL
            END
        """)
        
        # Drop the old integer column
        cr.execute("""
            ALTER TABLE vehicle_vehicle 
            DROP COLUMN year
        """)
        
        # Rename the temp column to year
        cr.execute("""
            ALTER TABLE vehicle_vehicle 
            RENAME COLUMN year_temp TO year
        """)
        
        _logger.info("Successfully converted year from Integer to Date")
    else:
        _logger.info("Year column is already date type or doesn't exist, skipping migration")
