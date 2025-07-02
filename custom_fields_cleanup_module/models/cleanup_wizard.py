# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CustomFieldsCleanupWizard(models.TransientModel):
    _name = 'custom.fields.cleanup.wizard'
    _description = 'Custom Fields Cleanup Wizard'

    state = fields.Selection([
        ('draft', 'Ready to Clean'),
        ('done', 'Cleanup Complete')
    ], default='draft')
    
    log_message = fields.Text("Cleanup Log", readonly=True)

    def action_cleanup_fields(self):
        """Perform the cleanup of orphaned references."""
        
        log_messages = []
        log_messages.append("=== Starting Custom Fields Cleanup ===\n")
        
        try:
            # 1. Fix orphaned sale_order_type_id references
            log_messages.append("1. Checking orphaned sale_order_type_id references...")
            
            # Check if sale_order_type table exists
            self.env.cr.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'sale_order_type'
                );
            """)
            
            table_exists = self.env.cr.fetchone()[0]
            
            if not table_exists:
                log_messages.append("   ⚠️  sale_order_type table does not exist, setting all references to NULL")
                self.env.cr.execute("""
                    UPDATE account_move 
                    SET sale_order_type_id = NULL 
                    WHERE sale_order_type_id IS NOT NULL;
                """)
                log_messages.append(f"   ✅ Set {self.env.cr.rowcount} orphaned sale_order_type_id references to NULL")
            else:
                # Fix orphaned references
                self.env.cr.execute("""
                    UPDATE account_move 
                    SET sale_order_type_id = NULL 
                    WHERE sale_order_type_id IS NOT NULL 
                    AND sale_order_type_id NOT IN (SELECT id FROM sale_order_type);
                """)
                if self.env.cr.rowcount > 0:
                    log_messages.append(f"   ✅ Fixed {self.env.cr.rowcount} orphaned sale_order_type_id references")
                else:
                    log_messages.append("   ✅ No orphaned sale_order_type_id references found")
            
            # 2. Fix orphaned project references
            log_messages.append("\n2. Checking orphaned project references...")
            self.env.cr.execute("""
                UPDATE account_move 
                SET project = NULL 
                WHERE project IS NOT NULL 
                AND project NOT IN (SELECT id FROM product_template);
            """)
            if self.env.cr.rowcount > 0:
                log_messages.append(f"   ✅ Fixed {self.env.cr.rowcount} orphaned project references")
            else:
                log_messages.append("   ✅ No orphaned project references found")
            
            # 3. Fix orphaned unit references
            log_messages.append("\n3. Checking orphaned unit references...")
            self.env.cr.execute("""
                UPDATE account_move 
                SET unit = NULL 
                WHERE unit IS NOT NULL 
                AND unit NOT IN (SELECT id FROM product_product);
            """)
            if self.env.cr.rowcount > 0:
                log_messages.append(f"   ✅ Fixed {self.env.cr.rowcount} orphaned unit references")
            else:
                log_messages.append("   ✅ No orphaned unit references found")
            
            # 4. Fix orphaned buyer references
            log_messages.append("\n4. Checking orphaned buyer references...")
            self.env.cr.execute("""
                UPDATE account_move 
                SET buyer = NULL 
                WHERE buyer IS NOT NULL 
                AND buyer NOT IN (SELECT id FROM res_partner);
            """)
            if self.env.cr.rowcount > 0:
                log_messages.append(f"   ✅ Fixed {self.env.cr.rowcount} orphaned buyer references")
            else:
                log_messages.append("   ✅ No orphaned buyer references found")
            
            # 5. Fix alternative field names
            alt_fields = [
                ('project_id', 'product_template'),
                ('unit_id', 'product_product'),
                ('buyer_id', 'res_partner')
            ]
            
            for field_name, ref_table in alt_fields:
                log_messages.append(f"\n5. Checking orphaned {field_name} references...")
                
                # Check if column exists first
                self.env.cr.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'account_move' 
                        AND column_name = '{field_name}'
                    );
                """)
                
                column_exists = self.env.cr.fetchone()[0]
                
                if column_exists:
                    self.env.cr.execute(f"""
                        UPDATE account_move 
                        SET {field_name} = NULL 
                        WHERE {field_name} IS NOT NULL 
                        AND {field_name} NOT IN (SELECT id FROM {ref_table});
                    """)
                    if self.env.cr.rowcount > 0:
                        log_messages.append(f"   ✅ Fixed {self.env.cr.rowcount} orphaned {field_name} references")
                    else:
                        log_messages.append(f"   ✅ No orphaned {field_name} references found")
                else:
                    log_messages.append(f"   ℹ️  Column {field_name} does not exist in account_move")
            
            # 6. Clean up duplicate field definitions
            log_messages.append("\n6. Checking for duplicate field definitions...")
            
            field_names = ['sale_order_type_id', 'project', 'unit', 'buyer', 'project_id', 'unit_id', 'buyer_id']
            total_removed = 0
            
            for field_name in field_names:
                duplicate_fields = self.env['ir.model.fields'].search([
                    ('model', '=', 'account.move'),
                    ('name', '=', field_name)
                ])
                
                if len(duplicate_fields) > 1:
                    # Keep the first one, remove the rest
                    fields_to_remove = duplicate_fields[1:]
                    log_messages.append(f"   ⚠️  Found {len(duplicate_fields)} definitions for {field_name}, removing {len(fields_to_remove)} duplicates")
                    fields_to_remove.unlink()
                    total_removed += len(fields_to_remove)
            
            if total_removed > 0:
                log_messages.append(f"   ✅ Removed {total_removed} duplicate field definitions")
            else:
                log_messages.append("   ✅ No duplicate field definitions found")
            
            # 7. Clean up orphaned ir_model_data entries
            log_messages.append("\n7. Cleaning up orphaned ir_model_data entries...")
            
            if table_exists:
                self.env.cr.execute("""
                    DELETE FROM ir_model_data 
                    WHERE model = 'sale.order.type' 
                    AND res_id IS NOT NULL 
                    AND res_id NOT IN (SELECT id FROM sale_order_type);
                """)
                if self.env.cr.rowcount > 0:
                    log_messages.append(f"   ✅ Cleaned up {self.env.cr.rowcount} orphaned ir_model_data entries")
                else:
                    log_messages.append("   ✅ No orphaned ir_model_data entries found")
            else:
                log_messages.append("   ℹ️  Skipping ir_model_data cleanup (sale_order_type table doesn't exist)")
            
            # 8. Fix missing paper format for osus_invoice_report
            log_messages.append("\n8. Fixing missing paper format for osus_invoice_report...")
            
            # Check if the external ID exists
            existing_paperformat_xmlid = self.env['ir.model.data'].search([
                ('module', '=', 'osus_invoice_report'),
                ('name', '=', 'paperformat_osus_invoice'),
                ('model', '=', 'report.paperformat')
            ])
            
            if not existing_paperformat_xmlid:
                # Look for existing paper format with similar name
                existing_format = self.env['report.paperformat'].search([
                    ('name', 'ilike', 'OSUS%'),
                ], limit=1)
                
                if existing_format:
                    log_messages.append(f"   Found existing paper format: {existing_format.name}")
                    # Create missing external ID
                    self.env['ir.model.data'].create({
                        'module': 'osus_invoice_report',
                        'name': 'paperformat_osus_invoice',
                        'model': 'report.paperformat',
                        'res_id': existing_format.id,
                        'noupdate': False,
                    })
                    log_messages.append("   ✅ Created missing external ID for existing paper format")
                else:
                    # Create new paper format
                    log_messages.append("   Creating new OSUS paper format...")
                    new_format = self.env['report.paperformat'].create({
                        'name': 'OSUS Invoice Format',
                        'format': 'A4',
                        'orientation': 'Portrait',
                        'margin_top': 50,
                        'margin_bottom': 50,
                        'margin_left': 10,
                        'margin_right': 10,
                        'header_line': False,
                        'header_spacing': 40,
                        'dpi': 90,
                    })
                    
                    # Create external ID
                    self.env['ir.model.data'].create({
                        'module': 'osus_invoice_report',
                        'name': 'paperformat_osus_invoice',
                        'model': 'report.paperformat',
                        'res_id': new_format.id,
                        'noupdate': False,
                    })
                    log_messages.append(f"   ✅ Created new paper format: {new_format.name}")
            else:
                log_messages.append("   ✅ Paper format external ID already exists")
            
            log_messages.append("\n=== Cleanup Completed Successfully! ===")
            log_messages.append("\n🎉 You can now restart Odoo. The '_unknown' object error should be resolved.")
            
            self.log_message = '\n'.join(log_messages)
            self.state = 'done'
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'custom.fields.cleanup.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'context': self.env.context,
            }
            
        except Exception as e:
            error_msg = f"❌ Error during cleanup: {str(e)}"
            log_messages.append(f"\n{error_msg}")
            self.log_message = '\n'.join(log_messages)
            _logger.error(error_msg)
            raise UserError(f"Cleanup failed: {str(e)}")

    def action_close(self):
        """Close the wizard."""
        return {'type': 'ir.actions.act_window_close'}
