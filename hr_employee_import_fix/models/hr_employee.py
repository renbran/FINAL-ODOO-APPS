# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, vals):
        """Override create to handle missing resource_id gracefully and partner name conflicts"""
        # Handle transaction rollback if needed
        try:
            # Handle partner name uniqueness constraint BEFORE creating employee
            if 'name' in vals and vals['name']:
                original_name = vals['name'].upper()
                vals['name'] = self._ensure_unique_partner_name(original_name)
                _logger.info(f"Employee name processed: '{original_name}' -> '{vals['name']}'")
            
            # If resource_id is provided but doesn't exist, handle it
            if 'resource_id' in vals and vals.get('resource_id'):
                resource_id = vals['resource_id']
                
                # Check if resource exists
                resource_exists = self.env['resource.resource'].browse(resource_id).exists()
                
                if not resource_exists:
                    _logger.warning(f"Resource ID {resource_id} not found, creating new resource record")
                    
                    # Create a new resource record
                    resource_vals = {
                        'name': vals.get('name', f'Resource for Employee'),
                        'resource_type': 'user',
                        'company_id': vals.get('company_id') or self.env.company.id,
                        'active': True,
                    }
                    
                    # If the ID was specific, try to create with that ID
                    try:
                        resource_vals['id'] = resource_id
                        new_resource = self.env['resource.resource'].create(resource_vals)
                        _logger.info(f"Created resource record with ID {resource_id}")
                    except Exception as e:
                        # If we can't create with specific ID, create without and update vals
                        del resource_vals['id']
                        new_resource = self.env['resource.resource'].create(resource_vals)
                        vals['resource_id'] = new_resource.id
                        _logger.info(f"Created resource record with new ID {new_resource.id}")
            
            # If no resource_id provided, let Odoo handle it normally
            elif 'resource_id' not in vals:
                # Odoo will auto-create resource record
                pass
            
            return super(HrEmployee, self).create(vals)
            
        except Exception as e:
            _logger.error(f"Error creating employee: {str(e)}")
            
            # Handle partner name constraint violations specifically
            if "duplicate key value violates unique constraint" in str(e) and "res_partner_name_uniqu" in str(e):
                _logger.warning("Partner name constraint violation, attempting to resolve...")
                # Rollback the transaction to clear the error state
                try:
                    self.env.cr.rollback()
                except:
                    pass
                if 'name' in vals:
                    # Try to find alternative name
                    original_name = vals['name'].upper()
                    vals['name'] = self._ensure_unique_partner_name(original_name, attempt=2)
                    _logger.info(f"Retrying with name: {vals['name']}")
                    return self.create(vals)
            
            # Handle transaction aborted errors
            if "current transaction is aborted" in str(e):
                _logger.warning("Transaction aborted, rolling back and retrying...")
                try:
                    self.env.cr.rollback()
                except:
                    pass
                # Retry the operation
                return self.create(vals)
            
            # If all else fails, remove resource_id and let Odoo auto-create
            if 'resource_id' in vals:
                _logger.warning("Removing resource_id from vals and letting Odoo auto-create")
                # Rollback transaction before retry
                try:
                    self.env.cr.rollback()
                except:
                    pass
                del vals['resource_id']
                return super(HrEmployee, self).create(vals)
            else:
                raise

    def _ensure_unique_partner_name(self, name, attempt=1):
        """
        Ensure partner name is unique by checking existing partners
        and appending suffixes if necessary
        """
        if not name:
            return name
            
        upper_name = name.upper()
        
        # Check if name already exists
        existing_partner = self.env['res.partner'].search([('name', '=', upper_name)], limit=1)
        
        if not existing_partner:
            return upper_name
        
        # Name exists, try alternatives
        _logger.info(f"Partner name '{upper_name}' already exists, generating alternative...")
        
        # Try various suffix strategies
        suffixes_to_try = [
            f' (EMP-{attempt})',
            f' ({attempt})',
            ' (EMPLOYEE)',
            f' (STAFF-{attempt})',
            f' (HR-{attempt})'
        ]
        
        for suffix in suffixes_to_try:
            alternative_name = upper_name + suffix
            existing = self.env['res.partner'].search([('name', '=', alternative_name)], limit=1)
            if not existing:
                _logger.info(f"Using alternative name: {alternative_name}")
                return alternative_name
        
        # If all else fails, add timestamp-based suffix
        import time
        timestamp_suffix = f' (T{int(time.time() % 10000)})'
        final_name = upper_name + timestamp_suffix
        _logger.info(f"Using timestamp-based name: {final_name}")
        return final_name

    @api.model
    def safe_bulk_create(self, employees_data):
        """
        Safe method for bulk creating employees with constraint handling
        
        Args:
            employees_data (list): List of employee dictionaries
            
        Returns:
            dict: Results with created employees and errors
        """
        results = {
            'created': [],
            'errors': [],
            'total_processed': 0,
            'success_count': 0,
            'error_count': 0
        }
        
        _logger.info(f"Starting bulk employee import for {len(employees_data)} employees")
        
        for employee_data in employees_data:
            results['total_processed'] += 1
            
            # Use savepoint for each employee to isolate transaction errors
            savepoint_name = f"employee_import_{results['total_processed']}"
            
            try:
                # Create savepoint
                self.env.cr.execute(f"SAVEPOINT {savepoint_name}")
                
                # Clean the data (includes name uniqueness check)
                clean_data = self._clean_employee_data(employee_data)
                _logger.info(f"Processing employee {results['total_processed']}: {clean_data.get('name', 'Unknown')}")
                
                # Create employee
                employee = self.create(clean_data)
                results['created'].append({
                    'id': employee.id,
                    'name': employee.name,
                    'employee_number': employee.employee_number or '',
                })
                results['success_count'] += 1
                
                # Release savepoint on success
                self.env.cr.execute(f"RELEASE SAVEPOINT {savepoint_name}")
                _logger.info(f"Successfully created employee: {employee.name}")
                
            except Exception as e:
                error_msg = str(e)
                
                # Rollback to savepoint to clear error state
                try:
                    self.env.cr.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                    _logger.info(f"Rolled back to savepoint for employee {results['total_processed']}")
                except Exception as rollback_error:
                    # If savepoint rollback fails, do full rollback
                    _logger.warning(f"Savepoint rollback failed, doing full rollback: {str(rollback_error)}")
                    try:
                        self.env.cr.rollback()
                    except:
                        pass
                
                results['errors'].append({
                    'data': employee_data,
                    'error': error_msg,
                    'row': results['total_processed']
                })
                results['error_count'] += 1
                _logger.error(f"Error creating employee at row {results['total_processed']}: {error_msg}")
        
        _logger.info(f"Bulk import complete: {results['success_count']} created, {results['error_count']} errors")
        return results

    def _clean_employee_data(self, data):
        """
        Clean employee data to prevent constraint violations
        
        Args:
            data (dict): Raw employee data
            
        Returns:
            dict: Cleaned employee data
        """
        cleaned_data = data.copy()
        
        # Handle partner name uniqueness constraint FIRST
        if 'name' in cleaned_data and cleaned_data['name']:
            original_name = cleaned_data['name']
            cleaned_data['name'] = self._ensure_unique_partner_name(original_name)
            if original_name != cleaned_data['name']:
                _logger.info(f"Cleaned employee name: '{original_name}' -> '{cleaned_data['name']}'")
        
        # Handle resource_id issues
        if 'resource_id' in cleaned_data:
            resource_id = cleaned_data['resource_id']
            if resource_id:
                # Check if it's a valid integer
                try:
                    resource_id = int(resource_id)
                    cleaned_data['resource_id'] = resource_id
                except (ValueError, TypeError):
                    # If not a valid integer, remove it
                    del cleaned_data['resource_id']
            else:
                # If empty, remove it
                del cleaned_data['resource_id']
        
        # Handle other potential foreign key issues
        foreign_key_fields = {
            'company_id': 'res.company',
            'department_id': 'hr.department', 
            'job_id': 'hr.job',
            'parent_id': 'hr.employee',
            'coach_id': 'hr.employee',
            'resource_calendar_id': 'resource.calendar',
            'user_id': 'res.users',
        }
        
        for field, model in foreign_key_fields.items():
            if field in cleaned_data and cleaned_data[field]:
                try:
                    record_id = int(cleaned_data[field])
                    # Check if record exists
                    if not self.env[model].browse(record_id).exists():
                        _logger.warning(f"Referenced {model} record {record_id} not found, removing {field}")
                        del cleaned_data[field]
                except (ValueError, TypeError):
                    # If not a valid integer, try to find by name
                    if isinstance(cleaned_data[field], str):
                        # Try to find record by name
                        if model == 'hr.department':
                            dept = self.env['hr.department'].search([('name', '=', cleaned_data[field])], limit=1)
                            cleaned_data[field] = dept.id if dept else False
                        elif model == 'hr.job':
                            job = self.env['hr.job'].search([('name', '=', cleaned_data[field])], limit=1)
                            cleaned_data[field] = job.id if job else False
                        # Add more name-based lookups as needed
                    
                    if not cleaned_data.get(field):
                        del cleaned_data[field]
        
        return cleaned_data

    @api.model
    def fix_existing_duplicate_partners(self):
        """
        Fix existing duplicate partner names in the database
        This should be run before importing new employees
        """
        _logger.info("Starting fix for existing duplicate partner names...")
        
        # Find duplicate partner names using SQL for better performance
        self.env.cr.execute("""
            SELECT name, COUNT(*), array_agg(id ORDER BY id) as ids
            FROM res_partner 
            WHERE name IS NOT NULL 
            GROUP BY name 
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC
        """)
        
        duplicates = self.env.cr.fetchall()
        _logger.info(f"Found {len(duplicates)} duplicate partner name groups")
        
        fixed_count = 0
        
        for name, count, ids in duplicates:
            _logger.info(f"Fixing duplicate name '{name}' with {count} records: {ids}")
            
            # Keep the first record with original name, rename others
            keep_id = ids[0]
            duplicate_ids = ids[1:]
            
            for i, partner_id in enumerate(duplicate_ids, 1):
                try:
                    partner = self.env['res.partner'].browse(partner_id)
                    if partner.exists():
                        # Generate unique name
                        if partner.email:
                            # Use email-based naming if available
                            email_part = partner.email.split('@')[0].upper()
                            new_name = f"{name} ({email_part})"
                        else:
                            # Use counter-based naming
                            new_name = f"{name} ({i})"
                        
                        # Ensure the new name is also unique
                        counter = 1
                        original_new_name = new_name
                        while self.env['res.partner'].search([('name', '=', new_name)], limit=1):
                            new_name = f"{original_new_name}-{counter}"
                            counter += 1
                        
                        # Update the partner name
                        partner.write({'name': new_name})
                        _logger.info(f"Renamed partner {partner_id}: '{name}' -> '{new_name}'")
                        fixed_count += 1
                        
                except Exception as e:
                    _logger.error(f"Error fixing partner {partner_id}: {str(e)}")
        
        return {
            'fixed_count': fixed_count,
            'message': f'Fixed {fixed_count} duplicate partner names',
            'duplicates_found': len(duplicates)
        }


class HrEmployeeImportWizard(models.TransientModel):
    _name = 'hr.employee.import.wizard'
    _description = 'Employee Import Wizard'

    import_file = fields.Binary('Import File', required=True)
    filename = fields.Char('Filename')
    skip_errors = fields.Boolean('Skip Errors', default=True, 
                                help="Continue importing even if some records fail")
    
    def import_employees(self):
        """
        Import employees from uploaded file
        """
        if not self.import_file:
            raise UserError(_('Please upload a file to import'))
        
        # This is a basic implementation - you'd need to add CSV/Excel parsing
        # For now, this shows the structure
        
        try:
            # Parse file (implement CSV/Excel parsing here)
            employees_data = []  # This would be populated from file
            
            # Use safe bulk create
            results = self.env['hr.employee'].safe_bulk_create(employees_data)
            
            # Show results
            message = f"""
            Import Results:
            - Total processed: {results['total_processed']}
            - Successfully created: {results['success_count']}
            - Errors: {results['error_count']}
            """
            
            if results['errors']:
                error_details = "\n".join([f"Row {err['row']}: {err['error']}" 
                                         for err in results['errors'][:10]])  # Show first 10 errors
                message += f"\n\nFirst few errors:\n{error_details}"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Import Complete'),
                    'message': message,
                    'type': 'success' if results['error_count'] == 0 else 'warning',
                    'sticky': True,
                }
            }
            
        except Exception as e:
            raise UserError(_('Import failed: %s') % str(e))
