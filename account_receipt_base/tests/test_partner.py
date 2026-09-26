# Copyright 2023 Simone Rubino - TAKOBI
# Copyright 2026 Francesco Ballerini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPartner(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner_model = cls.env["res.partner"]
        partner_id, _partner_name = partner_model.name_create("Test partner")
        cls.partner = partner_model.browse(partner_id)

    def test_partner_total_receipts_invoiced(self):
        self.assertEqual(
            self.partner.total_receipts_invoiced,
            0,
        )

        receipt = self.init_invoice(
            "out_receipt",
            partner=self.partner,
            post=True,
            products=self.product_a,
        )

        self.assertEqual(
            self.partner.total_receipts_invoiced,
            receipt.amount_untaxed,
        )

    def test_partner_view_receipts(self):
        receipt = self.init_invoice(
            "out_receipt",
            partner=self.partner,
            post=True,
            products=self.product_a,
        )

        receipts_action = self.partner.action_view_partner_receipts()
        receipts_model = receipts_action["res_model"]
        receipts_domain = receipts_action["domain"]
        receipts = self.env[receipts_model].search(receipts_domain)

        self.assertEqual(
            receipts,
            receipt,
        )
