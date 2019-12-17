# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestAccountInvoiceSearchByReference(TransactionCase):
    def setUp(self):
        super(TestAccountInvoiceSearchByReference, self).setUp()
        self.par_model = self.env["res.partner"]
        self.acc_model = self.env["account.account"]
        self.inv_model = self.env["account.invoice"]
        self.inv_line_model = self.env["account.invoice.line"]

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

        self.invoice_line1 = self._create_inv_line(self.invoice_account.id)

        self.invoice1 = self._create_invoice(self.partner1, "Test", self.invoice_line1)

    def _create_partner(self):
        partner = self.par_model.create(
            {"name": "Test Partner", "supplier": True, "company_type": "company"}
        )
        return partner

    def _create_inv_line(self, account_id):
        inv_line = self.inv_line_model.create(
            {
                "name": "test invoice line",
                "account_id": account_id,
                "quantity": 1.0,
                "price_unit": 3.0,
                "product_id": self.env.ref("product.product_product_8").id,
            }
        )
        return inv_line

    def _create_invoice(self, partner, name, inv_line):
        invoice = self.inv_model.create(
            {
                "partner_id": partner.id,
                "name": name,
                "reference": "Test reference",
                "invoice_line_ids": [(4, inv_line.id)],
            }
        )
        return invoice

    def test_account_invoice_method(self):
        self.invoice1.action_invoice_open()
        self.invoice1.write({"reference": "Test"})
        check_method = self.invoice1.name_search(
            name="INV", operator="ilike", args=[("id", "in", self.invoice1.ids)]
        )
        self.assertEqual(check_method[0][0], self.invoice1.id)
        self.assertEqual(check_method[0][1][-4:], self.invoice1.name)
