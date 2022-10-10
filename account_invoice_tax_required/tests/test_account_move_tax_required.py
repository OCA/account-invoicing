# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import tagged

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceTaxRequired(TestAccountReconciliationCommon):
    def setUp(self):
        super(TestAccountInvoiceTaxRequired, self).setUp()

        self.account_invoice = self.env["account.move"]
        self.account_journal = self.env["account.journal"]
        self.journal = self.account_journal.create(
            {"code": "test", "name": "test", "type": "sale"}
        )
        self.partner = self.env.ref("base.res_partner_3")

        self.account_account = self.env["account.account"]
        self.account_rec1_id = self.account_account.create(
            dict(
                code="20000",
                name="customer account",
                account_type="asset_receivable",
                reconcile=True,
            )
        )
        self.product_product = self.env["product.product"]
        self.product = self.product_product.create(
            {
                "name": "Test",
                "categ_id": self.env.ref("product.product_category_all").id,
                "standard_price": 50,
                "list_price": 100,
                "type": "service",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                "description": "Test",
            }
        )

        invoice_line_data = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "quantity": 10.0,
                    "account_id": self.account_account.search(
                        [
                            (
                                "account_type",
                                "=",
                                "income",
                            )
                        ],
                        limit=1,
                    ).id,
                    "name": "product test 5",
                    "price_unit": 100.00,
                    "tax_ids": False,
                },
            )
        ]

        self.invoice = self.account_invoice.create(
            dict(
                name="Test Customer Invoice",
                journal_id=self.journal.id,
                partner_id=self.partner.id,
                invoice_line_ids=invoice_line_data,
                move_type="out_invoice",
            )
        )

    def test_exception(self):
        """Validate invoice without tax must raise exception"""
        with self.assertRaises(exceptions.UserError):
            self.invoice.with_context(test_tax_required=True).action_post()

    def test_without_exception(self):
        """Validate invoice without tax must raise exception"""
        self.invoice.invoice_line_ids[0].tax_ids = [(4, self.tax_cash_basis.id)]
        self.invoice.with_context(test_tax_required=True).action_post()
