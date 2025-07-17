# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, vals):
        """Override create to handle missing resource_id gracefully"""
        try:
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
            
            # If all else fails, remove resource_id and let Odoo auto-create
            if 'resource_id' in vals:
                _logger.warning("Removing resource_id from vals and letting Odoo auto-create")
                del vals['resource_id']
                return super(HrEmployee, self).create(vals)
            else:
                raise

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
        
        for employee_data in employees_data:
            results['total_processed'] += 1
            
            try:
                # Clean the data
                clean_data = self._clean_employee_data(employee_data)
                
                # Create employee
                employee = self.create(clean_data)
                results['created'].append({
                    'id': employee.id,
                    'name': employee.name,
                    'employee_number': employee.employee_number or '',
                })
                results['success_count'] += 1
                
            except Exception as e:
                error_msg = str(e)
                results['errors'].append({
                    'data': employee_data,
                    'error': error_msg,
                    'row': results['total_processed']
                })
                results['error_count'] += 1
                _logger.error(f"Error creating employee at row {results['total_processed']}: {error_msg}")
        
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
    def fix_orphaned_employees(self):
        """
        Fix existing employees with missing resource records
        """
        # Find employees with invalid resource_id
        employees = self.search([])
        fixed_count = 0
        
        for employee in employees:
            try:
                # Check if resource exists
                if not employee.resource_id.exists():
                    # Create new resource
                    resource_vals = {
                        'name': employee.name or f'Resource for {employee.employee_number}',
                        'resource_type': 'user',
                        'company_id': employee.company_id.id,
                        'active': employee.active,
                    }
                    new_resource = self.env['resource.resource'].create(resource_vals)
                    employee.resource_id = new_resource.id
                    fixed_count += 1
                    _logger.info(f"Fixed resource for employee {employee.name}")
            except Exception as e:
                _logger.error(f"Error fixing employee {employee.name}: {str(e)}")
        
        return {
            'fixed_count': fixed_count,
            'message': f'Fixed {fixed_count} employee records with missing resources'
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
