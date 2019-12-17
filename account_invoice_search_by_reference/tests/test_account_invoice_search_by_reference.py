# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceSearchByReference(TransactionCase):
    def setUp(self):
        super(TestAccountInvoiceSearchByReference, self).setUp()
        self.par_model = self.env["res.partner"]
        self.acc_model = self.env["account.account"]
        self.inv_model = self.env["account.move"]
        self.inv_line_model = self.env["account.move.line"]

        self.partner1 = self._create_partner()

        self.invoice_account = self.acc_model.search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )

        self.invoice1 = self._create_invoice(self.partner1)

        self.invoice_line1 = self._create_inv_line(
            self.invoice_account.id, self.invoice1.id
        )

    def _create_partner(self):
        partner = self.par_model.create(
            {"name": "Test Partner", "supplier_rank": 1, "company_type": "company"}
        )
        return partner

    def _create_invoice(self, partner):
        invoice = self.inv_model.create(
            {"partner_id": partner.id, "ref": "Test reference"}
        )
        return invoice

    def _create_inv_line(self, account_id, move_id):
        inv_line = self.inv_line_model.create(
            {
                "name": "test invoice line",
                "account_id": account_id,
                "quantity": 1.0,
                "price_unit": 3.0,
                "product_id": self.env.ref("product.product_product_8").id,
                "move_id": move_id,
            }
        )
        return inv_line

    def test_account_invoice_method(self):
        check_method1 = self.invoice1.name_search(
            name="TEST", operator="ilike", args=[("id", "in", self.invoice1.ids)]
        )
        self.assertEqual(check_method1[0][0], self.invoice1.id)
        self.invoice1.action_post()
        check_method2 = self.invoice1.name_search(
            name="MISC", operator="ilike", args=[("id", "in", self.invoice1.ids)]
        )
        self.assertEqual(check_method2[0][0], self.invoice1.id)
