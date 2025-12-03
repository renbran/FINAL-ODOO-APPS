# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
"""
Migration Script: v3.6.0 Post-Migration
Purpose: Remove deprecated fields and models after backup

This script runs AFTER the module is upgraded to clean up deprecated code.
"""
import logging
from psycopg2 import sql

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Post-migration: Remove deprecated fields and models

    Args:
        cr: Database cursor
        version: Module version after upgrade
    """
    _logger.info("="*80)
    _logger.info("Starting rental_management v3.6.0 POST-MIGRATION")
    _logger.info("="*80)

    # Step 1: Drop deprecated columns from property_details
    _drop_deprecated_property_columns(cr)

    # Step 2: Drop deprecated model tables
    _drop_deprecated_model_tables(cr)

    # Step 3: Clean up orphaned data
    _clean_orphaned_data(cr)

    # Step 4: Update sequences and constraints
    _update_database_constraints(cr)

    # Step 5: Vacuum and analyze tables
    _optimize_database(cr)

    # Step 6: Log completion statistics
    _log_completion_stats(cr)

    _logger.info("="*80)
    _logger.info("rental_management v3.6.0 POST-MIGRATION COMPLETED SUCCESSFULLY")
    _logger.info("="*80)


def _drop_deprecated_property_columns(cr):
    """Drop deprecated columns from property_details table"""
    _logger.info("Removing deprecated columns from property_details...")

    deprecated_columns = [
        # Deprecated Pricing
        'token_amount',
        'sale_price',
        'tenancy_price',

        # Deprecated Property Details
        'property_licence_no',

        # Deprecated Parent Property
        'is_parent_property',
        'parent_property_id',

        # Deprecated Nearby Connectivity (individual fields)
        'airport',
        'national_highway',
        'metro_station',
        'metro_city',
        'school',
        'hospital',
        'shopping_mall',
        'park',

        # Deprecated Tower Building
        'towers',
        'no_of_towers',
        'facilities',

        # Deprecated Parent Property Related Fields
        'parent_airport',
        'parent_national_highway',
        'parent_metro_station',
        'parent_metro_city',
        'parent_school',
        'parent_hospital',
        'parent_shopping_mall',
        'parent_park',
        'parent_zip',
        'parent_street',
        'parent_street2',
        'parent_city',
        'parent_city_id',
        'parent_country_id',
        'parent_state_id',
        'parent_website',
        'parent_amenities_ids',
        'parent_specification_ids',
        'parent_landlord_id',

        # Deprecated Property Info
        'construct_year',
        'buying_year',
        'address',
        'sold_invoice_id',
        'sold_invoice_state',

        # Deprecated Certificates
        'certificate_ids',

        # Deprecated Connectivity
        'nearby_connectivity_ids',

        # Deprecated Room Details
        'room_no',
        'total_square_ft',
        'usable_square_ft',

        # Deprecated Residential
        'residence_type',

        # Deprecated Industrial
        'industry_name',
        'industry_location',
        'industrial_used_for',
        'other_usages',
        'industrial_facilities',

        # Deprecated Land
        'land_name',
        'area_hector',
        'land_facilities',

        # Deprecated Commercial
        'commercial_name',
        'commercial_type',
        'used_for',
        'floor_commercial',
        'total_floor_commercial',
        'commercial_facilities',
        'other_use',

        # Deprecated Measurement
        'commercial_measurement_ids',
        'industrial_measurement_ids',
        'total_commercial_measure',
        'total_industrial_measure',

        # Deprecated Furnishing
        'furnishing',
    ]

    columns_dropped = 0
    columns_not_found = 0

    for column in deprecated_columns:
        # Check if column exists
        cr.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'property_details'
                AND column_name = %s
            )
        """, (column,))

        column_exists = cr.fetchone()[0]

        if column_exists:
            try:
                # Drop the column
                cr.execute(sql.SQL(
                    "ALTER TABLE property_details DROP COLUMN IF EXISTS {column} CASCADE"
                ).format(column=sql.Identifier(column)))

                columns_dropped += 1
                _logger.info(f"  ✓ Dropped column: property_details.{column}")

            except Exception as e:
                _logger.warning(f"  ⚠ Could not drop column {column}: {str(e)}")
        else:
            columns_not_found += 1

    _logger.info(f"Summary: Dropped {columns_dropped} columns, {columns_not_found} columns not found (may have been removed already)")


def _drop_deprecated_model_tables(cr):
    """Drop deprecated model tables"""
    _logger.info("Removing deprecated model tables...")

    deprecated_tables = [
        # Deprecated measurement models
        'property_commercial_measurement',
        'property_industrial_measurement',

        # Deprecated certificate models
        'certificate_type',
        'property_certificate',

        # Deprecated parent property model
        'parent_property',
    ]

    tables_dropped = 0

    for table_name in deprecated_tables:
        # Check if table exists
        cr.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """, (table_name,))

        table_exists = cr.fetchone()[0]

        if table_exists:
            try:
                # First, check if table has any data
                cr.execute(f"SELECT COUNT(*) FROM {table_name}")
                record_count = cr.fetchone()[0]

                if record_count > 0:
                    _logger.warning(
                        f"  ⚠ Table {table_name} contains {record_count} records. "
                        f"Data has been backed up to {table_name}_deprecated_backup"
                    )

                # Drop foreign key constraints first
                cr.execute(f"""
                    SELECT conname
                    FROM pg_constraint
                    WHERE conrelid = '{table_name}'::regclass
                """)
                constraints = cr.fetchall()
                for (constraint_name,) in constraints:
                    try:
                        cr.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name} CASCADE")
                    except Exception:
                        pass

                # Drop the table
                cr.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                tables_dropped += 1
                _logger.info(f"  ✓ Dropped table: {table_name}")

                # Also drop related many2many relation tables
                cr.execute(f"""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    AND tablename LIKE '%{table_name}%rel%'
                """)
                m2m_tables = cr.fetchall()
                for (m2m_table,) in m2m_tables:
                    cr.execute(f"DROP TABLE IF EXISTS {m2m_table} CASCADE")
                    _logger.info(f"  ✓ Dropped relation table: {m2m_table}")

            except Exception as e:
                _logger.error(f"  ✗ Failed to drop table {table_name}: {str(e)}")
        else:
            _logger.info(f"  ✓ Table {table_name} does not exist (already removed)")

    _logger.info(f"Summary: Dropped {tables_dropped} deprecated model tables")


def _clean_orphaned_data(cr):
    """Clean up orphaned data after deprecated field removal"""
    _logger.info("Cleaning up orphaned data...")

    # Clean up ir_model_data entries for deprecated models
    deprecated_models = [
        'property.commercial.measurement',
        'property.industrial.measurement',
        'certificate.type',
        'property.certificate',
        'parent.property',
    ]

    for model_name in deprecated_models:
        cr.execute("""
            DELETE FROM ir_model_data
            WHERE model = %s
        """, (model_name,))

        deleted_count = cr.rowcount
        if deleted_count > 0:
            _logger.info(f"  ✓ Cleaned {deleted_count} ir_model_data entries for {model_name}")

    # Clean up ir_model entries for deprecated models
    cr.execute("""
        DELETE FROM ir_model
        WHERE model = ANY(%s)
    """, (deprecated_models,))

    deleted_models = cr.rowcount
    if deleted_models > 0:
        _logger.info(f"  ✓ Cleaned {deleted_models} ir_model entries")

    # Clean up ir_model_fields entries for deprecated fields
    cr.execute("""
        DELETE FROM ir_model_fields
        WHERE model = 'property.details'
        AND name = ANY(%s)
    """, ([
        'token_amount', 'sale_price', 'tenancy_price', 'property_licence_no',
        'is_parent_property', 'parent_property_id', 'residence_type',
        'industry_name', 'land_name', 'commercial_name', 'furnishing',
    ],))

    deleted_fields = cr.rowcount
    if deleted_fields > 0:
        _logger.info(f"  ✓ Cleaned {deleted_fields} deprecated field definitions")

    # Clean up ir_ui_view entries that reference deprecated models
    cr.execute("""
        SELECT id, name
        FROM ir_ui_view
        WHERE model = ANY(%s)
    """, (deprecated_models,))

    deprecated_views = cr.fetchall()
    if deprecated_views:
        view_ids = [v[0] for v in deprecated_views]
        cr.execute("""
            DELETE FROM ir_ui_view
            WHERE id = ANY(%s)
        """, (view_ids,))
        _logger.info(f"  ✓ Cleaned {len(deprecated_views)} views for deprecated models")

    # Clean up ir_act_window entries
    cr.execute("""
        DELETE FROM ir_act_window
        WHERE res_model = ANY(%s)
    """, (deprecated_models,))

    deleted_actions = cr.rowcount
    if deleted_actions > 0:
        _logger.info(f"  ✓ Cleaned {deleted_actions} window actions for deprecated models")

    # Clean up menu items
    cr.execute("""
        DELETE FROM ir_ui_menu
        WHERE action LIKE '%,parent.property%'
        OR action LIKE '%,certificate.type%'
    """)

    deleted_menus = cr.rowcount
    if deleted_menus > 0:
        _logger.info(f"  ✓ Cleaned {deleted_menus} menu items for deprecated models")


def _update_database_constraints(cr):
    """Update database constraints after field removal"""
    _logger.info("Updating database constraints...")

    # Check for any remaining foreign key constraints pointing to dropped tables
    cr.execute("""
        SELECT conname, conrelid::regclass
        FROM pg_constraint
        WHERE confrelid IN (
            SELECT oid FROM pg_class
            WHERE relname IN (
                'parent_property',
                'certificate_type',
                'property_certificate',
                'property_commercial_measurement',
                'property_industrial_measurement'
            )
        )
    """)

    orphaned_constraints = cr.fetchall()
    for constraint_name, table_name in orphaned_constraints:
        try:
            cr.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name} CASCADE")
            _logger.info(f"  ✓ Dropped orphaned constraint: {constraint_name} on {table_name}")
        except Exception as e:
            _logger.warning(f"  ⚠ Could not drop constraint {constraint_name}: {str(e)}")


def _optimize_database(cr):
    """Optimize database after major changes"""
    _logger.info("Optimizing database...")

    # Vacuum and analyze property_details table
    try:
        # Note: VACUUM cannot run inside a transaction, so we log it for manual execution
        _logger.info("  ℹ Run manually after migration: VACUUM ANALYZE property_details;")

        # We can run ANALYZE inside transaction
        cr.execute("ANALYZE property_details")
        _logger.info("  ✓ Analyzed property_details table")

    except Exception as e:
        _logger.warning(f"  ⚠ Could not optimize tables: {str(e)}")


def _log_completion_stats(cr):
    """Log completion statistics"""
    _logger.info("Migration Completion Statistics:")

    # Count remaining columns in property_details
    cr.execute("""
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_name = 'property_details'
    """)
    remaining_columns = cr.fetchone()[0]
    _logger.info(f"  - property_details: {remaining_columns} columns remaining")

    # Count backup tables
    cr.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name LIKE '%deprecated_backup'
    """)
    backup_tables = cr.fetchone()[0]
    _logger.info(f"  - Backup tables created: {backup_tables}")

    # Check backup data size
    cr.execute("""
        SELECT
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
        FROM pg_tables
        WHERE tablename LIKE '%deprecated_backup'
        AND schemaname = 'public'
    """)
    backup_sizes = cr.fetchall()
    if backup_sizes:
        _logger.info("  - Backup table sizes:")
        for schema, table, size in backup_sizes:
            _logger.info(f"    • {table}: {size}")

    # Total properties
    cr.execute("SELECT COUNT(*) FROM property_details")
    total_properties = cr.fetchone()[0]
    _logger.info(f"  - Total properties: {total_properties}")

    # Log recovery information
    _logger.info("")
    _logger.info("📋 IMPORTANT: Backup Recovery Information")
    _logger.info("  All deprecated data has been backed up to *_deprecated_backup tables")
    _logger.info("  To restore data (if needed):")
    _logger.info("    1. Check ir.config.parameter with key 'rental_management.migration_3_6_0_rollback'")
    _logger.info("    2. Contact TechKhedut support for assistance")
    _logger.info("  Backup tables will be retained for 90 days before automatic cleanup")
    _logger.info("")
