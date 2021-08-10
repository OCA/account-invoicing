# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import date

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountInvoiceMerge(TransactionCase):
    """
        Tests for Account Invoice Merge.
    """

    def setUp(self):
        super(TestAccountInvoiceMerge, self).setUp()
        self.par_model = self.env["res.partner"]
        self.context = self.env["res.users"].context_get()
        self.acc_model = self.env["account.account"]
        self.inv_model = self.env["account.move"]
        self.wiz = self.env["invoice.merge"]

        self.partner1 = self._create_partner()
        self.partner2 = self._create_partner()
        self.tax_21 = self.env["account.tax"].create(
            {"name": "New Tax 21%", "amount": 21}
        )

        self.invoice1 = self._create_invoice(self.partner1, "A")
        self.invoice2 = self.invoice1.copy(default={"name": "B"})
        self.invoice3 = self._create_invoice(self.partner2, "C")

    def _create_partner(self):
        partner = self.par_model.create(
            {"name": "Test Partner", "company_type": "company"}
        )
        return partner

    def _create_invoice(self, partner, name, product_id=False):
        account_id = (
            self.env["account.account"]
            .search(
                [
                    (
                        "user_type_id",
                        "=",
                        self.env.ref("account.data_account_type_revenue").id,
                    )
                ],
                limit=1,
            )
            .id
        )
        line_values = [
            (
                0,
                0,
                {
                    "product_id": product_id
                    or self.env.ref("product.product_product_8").id,
                    "quantity": 1.0,
                    "account_id": account_id,
                    "price_unit": 3.00,
                    "tax_ids": [(6, 0, self.tax_21.ids)],
                },
            )
        ]
        invoice = self.inv_model.create(
            {
                "journal_id": self.env["account.journal"]
                .search([("type", "=", "sale")], limit=1)
                .id,
                "type": "out_invoice",
                "name": name,
                "partner_id": partner.id,
                "invoice_line_ids": line_values,
            }
        )
        return invoice

    def test_account_invoice_merge_1(self):
        self.assertEqual(len(self.invoice1.invoice_line_ids), 1)
        self.assertEqual(len(self.invoice2.invoice_line_ids), 1)
        start_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(start_inv), 2)

        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice2.id],
            active_model="account.move",
        ).create({})
        wiz_id.fields_view_get()
        action = wiz_id.merge_invoices()

        self.assertDictContainsSubset(
            {
                "type": "ir.actions.act_window",
                "binding_view_types": "list,form",
                "xml_id": "account.action_move_out_invoice_type",
            },
            action,
            "There was an error and the two invoices were not merged.",
        )

        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(end_inv), 1)
        self.assertEqual(len(end_inv.invoice_line_ids), 1)
        self.assertEqual(end_inv.invoice_line_ids[0].quantity, 2.0)
        self.assertEqual(end_inv.invoice_line_ids[0].tax_ids, self.tax_21)

    def test_account_invoice_merge_2(self):
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice3.id],
            active_model="account.move",
        ).create({})
        with self.assertRaises(UserError):
            wiz_id.fields_view_get()

    def test_account_invoice_merge_different_products(self):
        invoice = self._create_invoice(
            self.partner2, "D", product_id=self.env.ref("product.product_product_3").id
        )
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice3.id, invoice.id], active_model="account.move",
        ).create({})
        wiz_id.fields_view_get()
        wiz_id.merge_invoices()
        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner2.id)]
        )
        self.assertEqual(len(end_inv.invoice_line_ids), 2)
        self.assertEqual(end_inv.invoice_line_ids[0].quantity, 1.0)
        self.assertEqual(
            end_inv.invoice_line_ids[0].product_id,
            self.env.ref("product.product_product_8"),
        )
        self.assertEqual(end_inv.invoice_line_ids[1].quantity, 1.0)
        self.assertEqual(
            end_inv.invoice_line_ids[1].product_id,
            self.env.ref("product.product_product_3"),
        )

    def test_account_invoice_merge_invoice_payment_ref(self):
        self.invoice1.invoice_payment_ref = "XXX"
        self.invoice2.invoice_payment_ref = "YYY"
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice2.id],
            active_model="account.move",
            default_keep_references=True,
        ).create({})
        wiz_id.fields_view_get()
        wiz_id.merge_invoices()
        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(end_inv.invoice_line_ids), 1)
        self.assertIn(self.invoice1.invoice_payment_ref, end_inv.invoice_payment_ref)
        self.assertIn(self.invoice2.invoice_payment_ref, end_inv.invoice_payment_ref)

    def test_account_invoice_merge_invoice_origin(self):
        self.invoice1.invoice_origin = "XXX"
        self.invoice2.invoice_origin = "YYY"
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice2.id],
            active_model="account.move",
            default_keep_references=True,
        ).create({})
        wiz_id.fields_view_get()
        wiz_id.merge_invoices()
        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(end_inv.invoice_line_ids), 1)
        self.assertIn(self.invoice1.invoice_origin, end_inv.invoice_origin)
        self.assertIn(self.invoice2.invoice_origin, end_inv.invoice_origin)

    def test_account_invoice_merge_invoice_date(self):
        invoice_date = date.today().replace(day=10)
        wiz_id = self.wiz.with_context(
            active_ids=[self.invoice1.id, self.invoice2.id],
            active_model="account.move",
            default_date_invoice=invoice_date,
        ).create({})
        wiz_id.fields_view_get()
        wiz_id.merge_invoices()
        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(end_inv.invoice_date, invoice_date)

    def test_dirty_check(self):
        """ Check  """
        wiz_id = self.wiz.with_context(active_model="account.move")

        # Check with only one invoice
        with self.assertRaises(UserError):
            wiz_id.with_context(active_ids=[self.invoice1.id]).fields_view_get()

        # Check with a canceled invoice
        # Create and cancel the invoice
        invoice = self._create_invoice(self.partner1, "D")
        invoice.button_cancel()
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=[self.invoice1.id, invoice.id]
            ).fields_view_get()

        # Check with an another company
        # Create an invoice and change the company
        invoice = self._create_invoice(self.partner1, "E")
        new_company = self.env["res.company"].create({"name": "Hello World"})
        invoice.company_id = new_company.id
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=[self.invoice1.id, invoice.id]
            ).fields_view_get()

        # Check with two different partners
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=[self.invoice1.id, self.invoice3.id]
            ).fields_view_get()

    def test_account_invoice_merge_keep_references(self):
        partner = self._create_partner()
        invoice1 = self._create_invoice(partner, "/")
        invoice2 = self._create_invoice(partner, "/")
        wiz_id = self.wiz.with_context(
            active_ids=[invoice1.id, invoice2.id],
            active_model="account.move",
            default_keep_references=True,
        ).create({})
        wiz_id.fields_view_get()
        wiz_id.merge_invoices()
        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", partner.id)]
        )
        end_inv.post()

        invoice3 = self._create_invoice(partner, "/")
        invoice4 = self._create_invoice(partner, "/")
        wiz_id = self.wiz.with_context(
            active_ids=[invoice3.id, invoice4.id],
            active_model="account.move",
            default_keep_references=True,
        ).create({})
        wiz_id.fields_view_get()
        wiz_id.merge_invoices()
        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", partner.id)]
        )
        end_inv.post()
