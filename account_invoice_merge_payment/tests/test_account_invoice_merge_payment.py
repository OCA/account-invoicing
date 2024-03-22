# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestAccountInvoiceMergePayment(SavepointCase):
    """
    Tests for Account Invoice Merge.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.par_model = cls.env["res.partner"]
        cls.context = cls.env["res.users"].context_get()
        cls.acc_model = cls.env["account.account"]
        cls.inv_model = cls.env["account.move"]
        cls.inv_line_model = cls.env["account.move.line"]
        cls.wiz = cls.env["invoice.merge"]
        cls.product = cls.env.ref("product.product_product_8")
        cls.account_receive = cls.env.ref("account.data_account_type_receivable")
        cls.partner1 = cls._create_partner()
        cls.partner2 = cls._create_partner()
        cls.invoice_account = cls.acc_model.search(
            [("user_type_id", "=", cls.account_receive.id)],
            limit=1,
        )
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )

        cls.default_payment_mode = cls.env.ref(
            "account_payment_mode.payment_mode_inbound_dd1"
        )
        cls.payment_mode2 = cls.env.ref(
            "account_payment_mode.payment_mode_outbound_dd2"
        )

        cls.invoice1 = cls._create_invoice(cls.partner1, "A")
        cls.invoice2 = cls._create_invoice(cls.partner1, "B")
        cls.invoice3 = cls._create_invoice(cls.partner2, "C")
        cls.invoice4 = cls._create_invoice(cls.partner2, "D")

        cls.invoice_line1 = cls._create_inv_line(cls.invoice1)
        cls.invoice_line2 = cls._create_inv_line(cls.invoice2)
        cls.invoice_line3 = cls._create_inv_line(cls.invoice3)
        cls.invoice_line4 = cls._create_inv_line(cls.invoice4)

    def _create_partner(self):
        partner = self.par_model.create(
            {"name": "Test Partner", "supplier_rank": 1, "company_type": "company"}
        )
        return partner

    def _create_inv_line(self, invoice):
        lines = invoice.invoice_line_ids
        invoice.write(
            {
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "name": "test invoice line",
                            "quantity": 1.0,
                            "price_unit": 3.0,
                            "move_id": invoice.id,
                            "product_id": self.product.id,
                            "exclude_from_invoice_tab": False,
                        },
                    )
                ]
            }
        )
        return invoice.invoice_line_ids - lines

    def _create_invoice(self, partner, name, journal=False):
        if not journal:
            journal = self.journal
        invoice = self.inv_model.create(
            {
                "partner_id": partner.id,
                "name": name,
                "move_type": "out_invoice",
                "journal_id": journal.id,
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
        invoices = self.invoice1 | self.invoice2
        wiz_id = self.wiz.with_context(
            active_ids=invoices.ids,
            active_model=invoices._name,
        ).create({})
        wiz_id.fields_view_get()
        action = wiz_id.merge_invoices()

        self.assertEqual(
            action["type"],
            "ir.actions.act_window",
            "There was an error and the two invoices were not merged.",
        )
        self.assertEqual(
            action["xml_id"],
            "account.action_move_out_invoice_type",
            "There was an error and the two invoices were not merged.",
        )

        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(end_inv), 1)
        self.assertEqual(len(end_inv[0].invoice_line_ids), 1)
        self.assertEqual(end_inv[0].invoice_line_ids[0].quantity, 2.0)
        self.assertEqual(end_inv.payment_mode_id, self.invoice1.payment_mode_id)

    def test_account_invoice_merge_2(self):
        self.invoice4.write({"payment_mode_id": self.payment_mode2})
        invoices = self.invoice3 | self.invoice4
        self.assertNotEqual(
            self.invoice3.payment_mode_id, self.invoice4.payment_mode_id
        )
        wiz_id = self.wiz.with_context(
            active_ids=invoices.ids,
            active_model=invoices._name,
        ).create({})
        with self.assertRaises(UserError):
            wiz_id.fields_view_get()
