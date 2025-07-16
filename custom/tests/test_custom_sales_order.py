import odoo.tests
from odoo.tests.common import TransactionCase

class TestCustomSalesOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})

    def test_custom_fields_create(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'custom_field_1': 'test',
            'custom_field_2': 42,
            'custom_field_3': self.partner.id,
        })
        self.assertEqual(order.custom_field_1, 'TEST')
        self.assertEqual(order.custom_field_2, 42)
        self.assertEqual(order.custom_field_3, self.partner)

    def test_custom_fields_write(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        order.write({'custom_field_1': 'write_test'})
        self.assertEqual(order.custom_field_1, 'WRITE_TEST')
