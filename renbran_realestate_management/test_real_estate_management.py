import odoo
from odoo.tests.common import TransactionCase

class TestRealEstateManagement(TransactionCase):

    def setUp(self):
        super(TestRealEstateManagement, self).setUp()
        self.property_obj = self.env['property.property']
        self.offer_obj = self.env['property.offer']
        self.sale_obj = self.env['property.sale']
        self.partner_obj = self.env['res.partner']

    def test_property_creation(self):
        property = self.property_obj.create({
            'name': 'Test Property',
            'property_type': 'apartment',
            'total_area': 100,
            'property_price': 100000,
        })
        self.assertTrue(property, "Property should be created")
        self.assertEqual(property.state, 'available', "New property should be in available state")

    def test_offer_creation(self):
        property = self.property_obj.create({
            'name': 'Test Property for Offer',
            'property_type': 'apartment',
            'total_area': 100,
            'property_price': 100000,
        })
        customer = self.partner_obj.create({'name': 'Test Customer'})
        offer = self.offer_obj.create({
            'property_id': property.id,
            'partner_id': customer.id,
            'offer_price': 95000,
        })
        self.assertTrue(offer, "Offer should be created")
        self.assertEqual(offer.state, 'pending', "New offer should be in pending state")

    def test_property_sale(self):
        property = self.property_obj.create({
            'name': 'Test Property for Sale',
            'property_type': 'apartment',
            'total_area': 100,
            'property_price': 100000,
        })
        customer = self.partner_obj.create({'name': 'Test Customer for Sale'})
        sale = self.sale_obj.create({
            'property_id': property.id,
            'partner_id': customer.id,
            'sale_price': 100000,
            'start_date': fields.Date.today(),
        })
        self.assertTrue(sale, "Sale should be created")
        self.assertEqual(sale.state, 'draft', "New sale should be in draft state")
        
        # Confirm sale
        sale.action_confirm()
        self.assertEqual(sale.state, 'confirm', "Sale should be confirmed")
        self.assertEqual(property.state, 'sold', "Property should be marked as sold")

    # Add more test methods for other functionalities