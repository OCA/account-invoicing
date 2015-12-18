# -*- coding: utf-8 -*-
# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestFiscalPositionUpdate(common.TransactionCase):

    def setUp(self):
        super(TestFiscalPositionUpdate, self).setUp()
        tax_obj = self.env['account.tax']
        fp_obj = self.env['account.fiscal.position']
        self.product = self.env.ref("product.product_product_1")
        # create tax include 10
        self.tax_i_10 = tax_obj.create({"name": "ti10", "amount": 0.1,
                                        "price_include": True})
        # create tax include 20
        self.tax_i_20 = tax_obj.create({"name": "ti20", "amount": 0.2,
                                        "price_include": True})
        # create tax exclude 10
        self.tax_e_10 = tax_obj.create({"name": "te10", "amount": 0.1,
                                        "price_include": False})
        # create tax exclude 20
        self.tax_e_20 = tax_obj.create({"name": "te20", "amount": 0.2,
                                        "price_include": False})

        # create fp to map tax_i_10 on tax_i_20
        self.fp_i_10_to_i_20 = fp_obj.create(
            {"name": "ti10 to ti20",
             "tax_ids": [(0, 0, {"tax_src_id": self.tax_i_10.id,
                                 "tax_dest_id": self.tax_i_20.id})]})
        # create fp to map tax_i_20 on tax_e_10
        self.fp_i_20_to_e_10 = fp_obj.create(
            {"name": "ti20 to te10",
             "tax_ids": [(0, 0, {"tax_src_id": self.tax_i_20.id,
                                 "tax_dest_id": self.tax_e_10.id})]})
        # create fp to map tax e_10 on tax_e_20
        self.fp_e_10_to_e_20 = fp_obj.create(
            {"name": "te10 to te20",
             "tax_ids": [(0, 0, {"tax_src_id": self.tax_e_10.id,
                                 "tax_dest_id": self.tax_e_20.id})]})

    def test_fp_price_change(self):
        # create invoice
        self.product.taxes_id = [(6, 0, [self.tax_i_10.id])]
        invoice = self.env["account.invoice"].create(
            {"partner_id": self.env.ref("base.res_partner_3").id,
             "account_id": self.env.ref("account.a_recv").id,
             "invoice_line": [(0, 0,
                               {"product_id": self.product.id,
                                "name": "my line",
                                "price_unit": 110,
                                "invoice_line_tax_id": [(4, self.tax_i_10.id)]}
                               )]})
        self.assertEqual(invoice.invoice_line.invoice_line_tax_id.id,
                         self.tax_i_10.id)

        # change fiscal position to set fp_i_10_to_i_20
        invoice.fiscal_position = self.fp_i_10_to_i_20.id
        invoice.fiscal_position_change()
        self.assertEqual(invoice.invoice_line.invoice_line_tax_id.id,
                         self.tax_i_20.id)
        self.assertEqual(invoice.invoice_line.price_unit, 120)

        # change fiscal position to set fp_i_20_to_e_10
        self.product.taxes_id = [(6, 0, [self.tax_i_20.id])]
        invoice.fiscal_position = self.fp_i_20_to_e_10.id
        invoice.fiscal_position_change()
        self.assertEqual(invoice.invoice_line.invoice_line_tax_id.id,
                         self.tax_e_10.id)
        self.assertEqual(invoice.invoice_line.price_unit, 100)

        # change fiscal position to set fp_e_10_to_e_20
        self.product.taxes_id = [(6, 0, [self.tax_e_10.id])]
        invoice.fiscal_position = self.fp_e_10_to_e_20.id
        invoice.fiscal_position_change()
        self.assertEqual(invoice.invoice_line.invoice_line_tax_id.id,
                         self.tax_e_20.id)
        self.assertEqual(invoice.invoice_line.price_unit, 100)

        # reset fiscal position to False
        self.product.taxes_id = [(6, 0, [self.tax_i_10.id])]
        invoice.fiscal_position = False
        invoice.fiscal_position_change()
        self.assertEqual(invoice.invoice_line.invoice_line_tax_id.id,
                         self.tax_i_10.id)
        self.assertEqual(invoice.invoice_line.price_unit, 110)
