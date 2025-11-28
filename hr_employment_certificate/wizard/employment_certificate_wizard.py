# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmploymentCertificateWizard(models.TransientModel):
    _name = 'hr.employment.certificate.wizard'
    _description = 'Employment Certificate Wizard'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.context.get('default_employee_id'),
    )
    employee_name = fields.Char(
        string='Employee Name',
        related='employee_id.name',
        readonly=True,
    )
    passport_number = fields.Char(
        string='Passport Number',
        related='employee_id.passport_id',
        readonly=False,
    )
    job_position = fields.Char(
        string='Job Position',
        compute='_compute_job_position',
        store=True,
        readonly=False,
    )
    # Employment Status
    employment_status = fields.Selection([
        ('current', 'Current Employee'),
        ('resigned', 'Resigned/Former Employee'),
    ], string='Employment Status', default='current', required=True,
       compute='_compute_employment_status', store=True, readonly=False)
    
    join_date = fields.Date(
        string='Join Date',
        compute='_compute_contract_details',
        store=True,
        readonly=False,
    )
    end_date = fields.Date(
        string='End Date',
        compute='_compute_contract_details',
        store=True,
        readonly=False,
        help="Leave empty for current employees",
    )
    gross_salary = fields.Monetary(
        string='Gross Monthly Salary',
        compute='_compute_contract_details',
        store=True,
        readonly=False,
        currency_field='currency_id',
    )
    last_salary = fields.Monetary(
        string='Last Drawn Salary',
        compute='_compute_contract_details',
        store=True,
        readonly=False,
        currency_field='currency_id',
        help="For resigned employees",
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    purpose = fields.Char(
        string='Purpose',
        default='visa/bank/official purposes',
        required=True,
    )
    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.context_today,
        required=True,
    )
    reference_number = fields.Char(
        string='Reference Number',
        readonly=True,
    )
    signatory_name = fields.Char(
        string='Signatory Name',
        default=lambda self: self.env.user.name,
    )
    signatory_title = fields.Char(
        string='Signatory Title',
        default='HR Manager',
    )
    pronoun = fields.Selection([
        ('Mr.', 'Mr.'),
        ('Ms.', 'Ms.'),
        ('Mrs.', 'Mrs.'),
    ], string='Pronoun', default='Mr.')
    
    @api.depends('employee_id')
    def _compute_employment_status(self):
        """Determine if employee is current or resigned based on contract/departure."""
        for wizard in self:
            if wizard.employee_id:
                # Check if employee has active contract
                active_contract = self.env['hr.contract'].search([
                    ('employee_id', '=', wizard.employee_id.id),
                    ('state', '=', 'open'),
                ], limit=1)
                
                # Check departure reason if available
                if hasattr(wizard.employee_id, 'departure_reason_id') and wizard.employee_id.departure_reason_id:
                    wizard.employment_status = 'resigned'
                elif not active_contract:
                    # No active contract, check if any contract exists
                    any_contract = self.env['hr.contract'].search([
                        ('employee_id', '=', wizard.employee_id.id),
                    ], limit=1)
                    if any_contract and any_contract.state in ('close', 'cancel'):
                        wizard.employment_status = 'resigned'
                    else:
                        wizard.employment_status = 'current'
                else:
                    wizard.employment_status = 'current'
            else:
                wizard.employment_status = 'current'

    @api.depends('employee_id')
    def _compute_job_position(self):
        for wizard in self:
            if wizard.employee_id and wizard.employee_id.job_id:
                wizard.job_position = wizard.employee_id.job_id.name
            else:
                wizard.job_position = ''

    @api.depends('employee_id')
    def _compute_contract_details(self):
        for wizard in self:
            # First try to find an active contract
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', wizard.employee_id.id),
                ('state', '=', 'open'),
            ], limit=1, order='date_start desc')
            
            # If no active contract, find the most recent one
            if not contract:
                contract = self.env['hr.contract'].search([
                    ('employee_id', '=', wizard.employee_id.id),
                ], limit=1, order='date_end desc, date_start desc')
            
            if contract:
                wizard.join_date = contract.date_start
                wizard.gross_salary = contract.wage
                wizard.last_salary = contract.wage
                # Set end date if contract has ended
                if contract.date_end and contract.state in ('close', 'cancel'):
                    wizard.end_date = contract.date_end
                elif hasattr(wizard.employee_id, 'departure_date') and wizard.employee_id.departure_date:
                    wizard.end_date = wizard.employee_id.departure_date
                else:
                    wizard.end_date = False
            else:
                wizard.join_date = wizard.employee_id.create_date.date() if wizard.employee_id else False
                wizard.gross_salary = 0.0
                wizard.last_salary = 0.0
                wizard.end_date = False

    def _get_employee_pronoun_name(self):
        """Get the pronoun + last name format."""
        self.ensure_one()
        if self.employee_id and self.employee_id.name:
            name_parts = self.employee_id.name.strip().split()
            last_name = name_parts[-1] if name_parts else ''
            return f"{self.pronoun} {last_name}"
        return ''
    
    def _get_employment_period_text(self):
        """Get the employment period text (e.g., 'January 01, 2020 to Present' or 'January 01, 2020 to December 31, 2024')."""
        self.ensure_one()
        if self.employment_status == 'resigned' and self.end_date:
            return 'to'
        return 'to Present'

    def action_print_certificate(self):
        """Generate and print the employment certificate."""
        self.ensure_one()
        
        if not self.employee_id:
            raise UserError(_("Please select an employee."))
        
        # Generate reference number
        if not self.reference_number:
            sequence = self.env['ir.sequence'].next_by_code('hr.employment.certificate')
            self.reference_number = sequence or f"CERT-{fields.Date.today().year}"
        
        # Return the report action
        return self.env.ref(
            'hr_employment_certificate.action_report_employment_certificate'
        ).report_action(self)
