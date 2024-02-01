# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# Copyright 2024 - Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import tagged

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceTaxRequired(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceTaxRequired, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )

        cls.account_invoice = cls.env["account.move"]
        cls.account_journal = cls.env["account.journal"]
        cls.journal = cls.account_journal.create(
            {"code": "test", "name": "test", "type": "sale"}
        )
        cls.partner = cls.env.ref("base.res_partner_3")
        account_user_type = cls.env.ref("account.data_account_type_receivable")

        cls.account_account = cls.env["account.account"]
        cls.account_rec1_id = cls.account_account.create(
            dict(
                code="cust_acc",
                name="customer account",
                user_type_id=account_user_type.id,
                reconcile=True,
            )
        )
        cls.product_product = cls.env["product.product"]
        cls.product = cls.product_product.create(
            {
                "name": "Test",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "standard_price": 50,
                "list_price": 100,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "description": "Test",
            }
        )

        invoice_line_data = [
            (
                0,
                0,
                {
                    "product_id": cls.product.id,
                    "quantity": 10.0,
                    "account_id": cls.account_account.search(
                        [
                            (
                                "user_type_id",
                                "=",
                                cls.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    ).id,
                    "name": "product test 5",
                    "price_unit": 100.00,
                },
            )
        ]

        cls.invoice = cls.account_invoice.create(
            dict(
                name="Test Customer Invoice",
                journal_id=cls.journal.id,
                partner_id=cls.partner.id,
                invoice_line_ids=invoice_line_data,
                move_type="out_invoice",
            )
        )

    def test_exception(self):
        """Validate invoice without tax must raise exception"""
        with self.assertRaises(exceptions.RedirectWarning):
            self.invoice.with_context(test_tax_required=True).action_post()

    def test_mass_validation(self):
        wizard = (
            self.env["validate.account.move"]
            .with_context(
                test_tax_required=True,
                active_model="account.move",
                active_ids=self.invoice.ids,
            )
            .create({})
        )
        with self.assertRaises(exceptions.RedirectWarning):
            wizard.validate_move()

    def test_without_exception(self):
        """Validate invoice without tax must raise exception"""
        self.invoice.invoice_line_ids[0].tax_ids = [(4, self.tax_cash_basis.id)]
        self.invoice.with_context(test_tax_required=True).action_post()
