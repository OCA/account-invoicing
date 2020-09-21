# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestInvoicePaymentWarranty(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.invoice_model = cls.env["account.move"]
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product_1 = cls.env.ref("product.product_product_3")
        cls.product_2 = cls.env.ref("product.product_product_5")
        cls.account_warranty = cls.env["account.account"].create(
            {
                "code": "WR",
                "name": "Warranty Account",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_current_liabilities"
                ).id,
                "reconcile": True,
            }
        )
        # Enable retention feature
        cls.env.user.groups_id += cls.env.ref(
            "account_invoice_payment_warranty.group_payment_warranty"
        )
        cls.env.company.warranty_account_id = cls.account_warranty

        cls.account_revenue = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )
        cls.sale_journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        cls.purchase_journal = cls.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )

    def _create_invoice(self, is_warranty=False):
        cust_invoice = self.invoice_model.create(
            {
                "name": "Test Customer Invoice",
                "type": "out_invoice",
                "journal_id": self.sale_journal.id,
                "partner_id": self.partner.id,
                "is_warranty": is_warranty,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "quantity": 1.0,
                            "account_id": is_warranty
                            and self.account_warranty
                            or self.account_revenue.id,
                            "name": self.product_1.name,
                            "price_unit": 500.00,
                        },
                    )
                ],
            }
        )
        return cust_invoice

    def test_01_warranty_account(self):
        """ Warranty account must be set as allow reconciliation """
        self.env.company.warranty_account_id = False
        self.account_warranty.reconcile = False
        with self.assertRaises(ValidationError):
            self.env.company.warranty_account_id = self.account_warranty
        self.account_warranty.reconcile = True
        self.env.company.warranty_account_id = self.account_warranty

    def test_02_warranty_check_product(self):
        cust_invoice1 = self._create_invoice(is_warranty=True)
        cust_line = cust_invoice1.invoice_line_ids.with_context(
            {"check_move_validity": False}
        )
        self.assertEqual(cust_line.product_id, self.product_1)
        cust_line.product_id = self.product_2
        self.assertEqual(cust_line.product_id, self.product_2)

    def test_03_warranty_invoice(self):
        cust_invoice1 = self._create_invoice()
        self.assertFalse(cust_invoice1.is_warranty)
        self.assertEqual(len(cust_invoice1.invoice_line_ids), 1)
        with Form(cust_invoice1) as inv:
            inv.is_warranty = True
        self.assertTrue(cust_invoice1.is_warranty)
        self.assertEqual(len(cust_invoice1.invoice_line_ids), 0)

        cust_invoice2 = self._create_invoice(is_warranty=True)
        self.assertTrue(cust_invoice2.is_warranty)
        self.assertEqual(len(cust_invoice2.invoice_line_ids), 1)
        cust_invoice2.post()
        # register payment
        ctx = {
            "active_ids": [cust_invoice2.id],
            "active_id": cust_invoice2.id,
            "active_model": "account.move",
        }
        PaymentWizard = self.env["account.payment"]
        view_id = "account.view_account_payment_invoice_form"
        with Form(PaymentWizard.with_context(ctx), view=view_id) as f:
            payment = f.save()
        payment.post()
        self.assertEqual(cust_invoice2.invoice_payment_state, "paid")
        payment_moves = payment.move_line_ids.mapped("move_id")
        # return warranty
        ctx = {"default_type": "in_invoice"}
        view_id = "account.view_move_form"
        with Form(self.invoice_model.with_context(ctx), view=view_id) as f:
            f.journal_id = self.purchase_journal
            f.partner_id = self.partner
        cust_invoice3 = f.save()
        res = cust_invoice3._onchange_domain_warranty_move_ids()
        warranty_move_list = res["domain"]["warranty_move_ids"][0][2]
        warranty_move_ids = self.env["account.move"].browse(warranty_move_list)
        #  Select retained moves type entry and out_invoice
        move_ids = warranty_move_ids | payment_moves
        with self.assertRaises(UserError):
            with Form(cust_invoice3, view=view_id) as f:
                for move in move_ids:
                    f.warranty_move_ids.add(move)
            cust_invoice3 = f.save()
        # Case normal return warranty
        with Form(cust_invoice3, view=view_id) as f:
            for move in warranty_move_ids:
                f.warranty_move_ids.add(move)
        cust_invoice3 = f.save()
        cust_invoice3.post()
