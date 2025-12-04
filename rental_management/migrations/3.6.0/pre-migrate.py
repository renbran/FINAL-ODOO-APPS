# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
"""
Migration Script: v3.6.0 Pre-Migration
Purpose: Backup deprecated data before cleanup

This script runs BEFORE the module is upgraded to prepare for deprecated field removal.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Pre-migration: Backup deprecated data before removal

    Args:
        cr: Database cursor
        version: Current module version before upgrade
    """
    _logger.info("="*80)
    _logger.info("Starting rental_management v3.6.0 PRE-MIGRATION")
    _logger.info("="*80)

    # Step 1: Check if deprecated fields exist
    _check_deprecated_fields_exist(cr)

    # Step 2: Backup deprecated property fields
    _backup_deprecated_property_fields(cr)

    # Step 3: Backup deprecated models data
    _backup_deprecated_models(cr)

    # Step 4: Log statistics
    _log_migration_stats(cr)

    _logger.info("="*80)
    _logger.info("rental_management v3.6.0 PRE-MIGRATION COMPLETED")
    _logger.info("="*80)


def _check_deprecated_fields_exist(cr):
    """Check if deprecated fields exist in database"""
    _logger.info("Checking for deprecated fields...")

    # Check property_details table for deprecated fields
    deprecated_fields = [
        'token_amount', 'sale_price', 'tenancy_price', 'property_licence_no',
        'is_parent_property', 'parent_property_id', 'airport', 'national_highway',
        'metro_station', 'metro_city', 'school', 'hospital', 'shopping_mall', 'park',
        'towers', 'no_of_towers', 'facilities', 'construct_year', 'buying_year',
        'address', 'sold_invoice_id', 'sold_invoice_state', 'room_no',
        'total_square_ft', 'usable_square_ft', 'residence_type', 'industry_name',
        'industry_location', 'industrial_used_for', 'other_usages', 'industrial_facilities',
        'land_name', 'area_hector', 'land_facilities', 'commercial_name',
        'commercial_type', 'used_for', 'floor_commercial', 'total_floor_commercial',
        'commercial_facilities', 'other_use', 'furnishing'
    ]

    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'property_details'
        AND column_name = ANY(%s)
    """, (deprecated_fields,))

    existing_fields = [row[0] for row in cr.fetchall()]

    if existing_fields:
        _logger.info(f"Found {len(existing_fields)} deprecated fields in property_details: {existing_fields}")
    else:
        _logger.info("No deprecated fields found in property_details (may have been removed already)")

    return existing_fields


def _backup_deprecated_property_fields(cr):
    """
    Backup deprecated property fields to archive table
    Only properties using these fields will be backed up
    """
    _logger.info("Backing up deprecated property fields...")

    # Create backup table if it doesn't exist
    cr.execute("""
        CREATE TABLE IF NOT EXISTS property_details_deprecated_backup (
            id SERIAL PRIMARY KEY,
            property_id INTEGER NOT NULL REFERENCES property_details(id) ON DELETE CASCADE,
            backup_date TIMESTAMP DEFAULT NOW(),
            deprecated_data JSONB,
            UNIQUE(property_id)
        )
    """)

    # Check which deprecated fields actually exist
    existing_fields = _check_deprecated_fields_exist(cr)

    if not existing_fields:
        _logger.info("No deprecated fields to backup")
        return

    # Build dynamic SQL to select only existing fields
    field_selects = ', '.join([
        f"'{field}', {field}" for field in existing_fields
    ])

    # Backup data from properties that have non-null deprecated field values
    backup_sql = f"""
        INSERT INTO property_details_deprecated_backup (property_id, deprecated_data)
        SELECT
            id as property_id,
            jsonb_build_object({field_selects}) as deprecated_data
        FROM property_details
        WHERE {' OR '.join([f'{field} IS NOT NULL' for field in existing_fields])}
        ON CONFLICT (property_id) DO UPDATE
        SET deprecated_data = EXCLUDED.deprecated_data,
            backup_date = NOW()
    """

    cr.execute(backup_sql)
    backup_count = cr.rowcount

    _logger.info(f"✓ Backed up {backup_count} properties with deprecated field data")

    # Log sample of backed up data
    if backup_count > 0:
        cr.execute("""
            SELECT property_id, deprecated_data
            FROM property_details_deprecated_backup
            LIMIT 3
        """)
        samples = cr.fetchall()
        _logger.info("Sample backed up data:")
        for prop_id, data in samples:
            _logger.info(f"  Property ID {prop_id}: {len(data)} fields backed up")


def _backup_deprecated_models(cr):
    """Backup deprecated models to archive tables"""
    _logger.info("Backing up deprecated models...")

    deprecated_models = {
        'property_commercial_measurement': [
            'id', 'shops', 'length', 'width', 'height', 'carpet_area',
            'commercial_measurement_id', 'no_of_unit', 'measure_unit'
        ],
        'property_industrial_measurement': [
            'id', 'asset', 'length', 'width', 'height', 'carpet_area',
            'industrial_measurement_id', 'no_of_unit', 'measure_unit'
        ],
        'certificate_type': ['id', 'type'],
        'property_certificate': [
            'id', 'type_id', 'expiry_date', 'responsible', 'note', 'property_id'
        ],
        'parent_property': [
            'id', 'name', 'image', 'company_id', 'type', 'zip', 'street',
            'street2', 'city', 'city_id', 'country_id', 'state_id', 'website'
        ],
    }

    for model_table, fields in deprecated_models.items():
        # Check if table exists
        cr.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """, (model_table,))

        table_exists = cr.fetchone()[0]

        if not table_exists:
            _logger.info(f"  ✓ Table {model_table} does not exist (already cleaned)")
            continue

        # Count records
        cr.execute(f"SELECT COUNT(*) FROM {model_table}")
        record_count = cr.fetchone()[0]

        if record_count == 0:
            _logger.info(f"  ✓ Table {model_table} is empty")
            continue

        # Create backup table
        backup_table = f"{model_table}_deprecated_backup"

        # Check which fields actually exist in the table
        cr.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
        """, (model_table,))

        existing_columns = [row[0] for row in cr.fetchall()]
        fields_to_backup = [f for f in fields if f in existing_columns]

        if not fields_to_backup:
            _logger.warning(f"  ⚠ No fields found to backup for {model_table}")
            continue

        fields_str = ', '.join(fields_to_backup)

        cr.execute(f"""
            CREATE TABLE IF NOT EXISTS {backup_table} (
                backup_id SERIAL PRIMARY KEY,
                backup_date TIMESTAMP DEFAULT NOW(),
                original_data JSONB
            )
        """)

        # Backup all records as JSON
        cr.execute(f"""
            INSERT INTO {backup_table} (original_data)
            SELECT row_to_json({model_table}.*)
            FROM {model_table}
        """)

        backed_up_count = cr.rowcount
        _logger.info(f"  ✓ Backed up {backed_up_count} records from {model_table} to {backup_table}")


def _log_migration_stats(cr):
    """Log statistics about the migration"""
    _logger.info("Migration Statistics:")

    # Count backed up properties
    cr.execute("SELECT COUNT(*) FROM property_details_deprecated_backup")
    property_backup_count = cr.fetchone()[0]
    _logger.info(f"  - Properties with deprecated data backed up: {property_backup_count}")

    # Count active properties
    cr.execute("SELECT COUNT(*) FROM property_details")
    total_properties = cr.fetchone()[0]
    _logger.info(f"  - Total properties in system: {total_properties}")

    # Count deprecated model backups
    deprecated_models = [
        'property_commercial_measurement_deprecated_backup',
        'property_industrial_measurement_deprecated_backup',
        'certificate_type_deprecated_backup',
        'property_certificate_deprecated_backup',
        'parent_property_deprecated_backup',
    ]

    for backup_table in deprecated_models:
        cr.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = '{backup_table}'
            )
        """)

        if cr.fetchone()[0]:
            cr.execute(f"SELECT COUNT(*) FROM {backup_table}")
            count = cr.fetchone()[0]
            if count > 0:
                _logger.info(f"  - {backup_table}: {count} records")


def _create_rollback_script(cr):
    """
    Create SQL script for rollback if needed
    This is saved to the database for emergency recovery
    """
    _logger.info("Creating rollback documentation...")

    rollback_sql = """
    -- ROLLBACK SCRIPT FOR v3.6.0 MIGRATION
    -- Run this script if you need to restore deprecated fields
    -- WARNING: This should only be used in emergency situations

    -- Step 1: Restore deprecated property fields from backup
    -- (Fields will need to be manually added back to the model first)

    -- Step 2: Restore property_details deprecated data
    -- UPDATE property_details p
    -- SET
    --     token_amount = (b.deprecated_data->>'token_amount')::numeric,
    --     sale_price = (b.deprecated_data->>'sale_price')::numeric
    --     -- Add other fields as needed
    -- FROM property_details_deprecated_backup b
    -- WHERE p.id = b.property_id;

    -- Step 3: Restore deprecated models from backup tables
    -- Contact TechKhedut support for assistance with model restoration

    """

    # Store rollback script in ir_config_parameter for reference
    cr.execute("""
        INSERT INTO ir_config_parameter (key, value, create_date, write_date, create_uid, write_uid)
        VALUES (
            'rental_management.migration_3_6_0_rollback',
            %s,
            NOW(),
            NOW(),
            1,
            1
        )
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (rollback_sql,))

    _logger.info("  ✓ Rollback documentation saved to ir.config.parameter")
    _logger.info("  Key: rental_management.migration_3_6_0_rollback")
