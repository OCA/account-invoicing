# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase
from openerp.exceptions import ValidationError


class TestAccountInvoiceGroupPicking(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceGroupPicking, cls).setUpClass()
        cls.category = cls.env['product.category'].create({
            'name': 'Test category',
            'type': 'normal',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product for test',
            'categ_id': cls.category.id,
            'default_code': 'TESTPROD01',
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner for test',
            'property_product_pricelist': cls.pricelist.id,
        })


    def test_defaults(self):
        pass
