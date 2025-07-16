import odoo.tests
from odoo.tests.common import TransactionCase

class TestOmDynamicReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.model = self.env['ir.model'].search([('model', '=', 'res.partner')], limit=1)

    def test_create_dynamic_report(self):
        report = self.env['om.dynamic.report'].create({
            'name': 'Test Report',
            'report_type': 'pdf',
            'model_id': self.model.id,
            'filter_domain': "[]",
        })
        self.assertEqual(report.name, 'Test Report')
        self.assertEqual(report.report_type, 'pdf')
        self.assertEqual(report.model_id, self.model)

    def test_generate_report(self):
        report = self.env['om.dynamic.report'].create({
            'name': 'Test Report',
            'report_type': 'pdf',
            'model_id': self.model.id,
        })
        self.assertTrue(report.generate_report())
