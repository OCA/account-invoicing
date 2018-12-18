# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()

        self.Wizard = self.env['wizard.update.invoice.supplierinfo']

        self.product_ipad = self.env.ref('product.product_product_4')
        self.partner = self.env.ref(
            'account_invoice_supplierinfo_update_discount.partner')
        self.invoice = self.env.ref(
            'account_invoice_supplierinfo_update_discount.invoice_discount')

    def test_invoice(self):
        # Call wizard and apply changes
        lines = self.invoice._get_update_supplierinfo_lines()

        wizard = self.Wizard.with_context(
            default_invoice_id=self.invoice.id,
            default_line_ids=lines).create({})
        wizard.update_supplierinfo()

        # Check creation of supplierinfo
        supplierinfos = self.product_ipad.seller_ids.filtered(
            lambda x: x.name == self.partner)

        self.assertEqual(
            len(supplierinfos), 1,
            "Creation of  supplierinfo failed")

        self.assertEqual(
            supplierinfos[0].discount, 25.0,
            "Discount has not been set when creating supplierinfo")

        # Change value from 25.0 to 33.0 and try update process
        self.invoice.invoice_line_ids[0].discount = 33.0
        self.invoice.supplierinfo_ok = False
        lines = self.invoice._get_update_supplierinfo_lines()

        wizard = self.Wizard.with_context(
            default_invoice_id=self.invoice.id,
            default_line_ids=lines).create({})
        wizard.update_supplierinfo()

        supplierinfos = self.product_ipad.seller_ids.filtered(
            lambda x: x.name == self.partner)

        self.assertEqual(
            len(supplierinfos), 1,
            "Update of  supplierinfo failed")

        self.assertEqual(
            supplierinfos[0].discount, 33.0,
            "Discount has not been set when updating supplierinfo")
