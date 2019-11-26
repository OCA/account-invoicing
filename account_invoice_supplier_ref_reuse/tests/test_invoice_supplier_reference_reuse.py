# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestInvoiceSupplierReferenceReuse(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {"name": "purchase_0", "code": "purchase0", "type": "purchase"}
        )
        cls.invoice_line_account = cls.env["account.account"].create(
            {
                "code": "PA1000",
                "name": "Test Payable Account",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        cls.invoice = cls._create_invoice_with_reference(cls, "ABC123")

    def _create_invoice_with_reference(self, reference):
        invoice = (
            self.env["account.move"]
            .with_context(default_journal_id=self.journal.id, test_no_refuse_ref=True)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_2").id,
                    "type": "in_invoice",
                    "ref": reference,
                }
            )
        )
        self.env["account.move.line"].create(
            {
                "product_id": self.env.ref("product.product_product_4").id,
                "quantity": 1.0,
                "price_unit": 0,
                "move_id": invoice.id,
                "name": "product that cost 100",
                "account_id": self.invoice_line_account.id,
            }
        )
        invoice.action_post()
        return invoice

    def test_01_reference_reuse(self):
        """ Check that reusing the reference number is possible """
        invoice2 = self._create_invoice_with_reference(self.invoice.ref)
        self.assertEqual(invoice2.ref, self.invoice.ref)
