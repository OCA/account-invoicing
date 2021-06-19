# Copyright 2021 Eder Brito - pingotecnologia.com.br

from odoo.tests import common


class TestAccountInvoiceInstallment(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        account100 = cls.env["account.account"].create(
            {
                "code": "100",
                "name": "Account 100",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        account200 = cls.env["account.account"].create(
            {
                "code": "200",
                "name": "Account 200",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        account300 = cls.env["account.account"].create(
            {
                "code": "300",
                "name": "Account 300",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
                "reconcile": True,
            }
        )
        account400 = cls.env["account.account"].create(
            {
                "code": "400",
                "name": "Account 400",
                "user_type_id": cls.env.ref("account.data_account_type_revenue").id,
                "reconcile": True,
            }
        )
        cls.partner_id = cls.env.ref("base.res_partner_12").id
        cls.env["account.journal"].create(
            {
                "name": "Journal 1",
                "code": "J1",
                "type": "sale",
                "company_id": cls.env.user.company_id.id,
            }
        )
        cls.in_move_lines = [
            (
                0,
                False,
                {
                    "name": "Test description #1",
                    "account_id": account200.id,
                    "quantity": 1.0,
                    "credit": 100.0,
                    "partner_id": cls.partner_id,
                },
            ),
            (
                0,
                False,
                {
                    "name": "Test description #2",
                    "account_id": account300.id,
                    "quantity": 1.0,
                    "debit": 100.0,
                    "partner_id": cls.partner_id,
                },
            ),
        ]
        cls.out_move_lines = [
            (
                0,
                False,
                {
                    "name": "Test description #1",
                    "account_id": account100.id,
                    "quantity": 1.0,
                    "credit": 100.0,
                    "partner_id": cls.partner_id,
                },
            ),
            (
                0,
                False,
                {
                    "name": "Test description #2",
                    "account_id": account400.id,
                    "quantity": 1.0,
                    "debit": 100.0,
                    "partner_id": cls.partner_id,
                },
            ),
        ]
        cls.invoice_in = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "in_invoice",
                "invoice_line_ids": cls.in_move_lines,
            }
        )

        cls.invoice_in.action_post()
        cls.invoice_in._compute_receivable_move_line_ids()

        cls.invoice_out = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": cls.out_move_lines,
            }
        )

        cls.invoice_out.action_post()
        cls.invoice_out._compute_payable_move_line_ids()

    def _test_installment(self):
        self.assertTrue(self.invoice_out.receivable_move_line_ids)
        self.assertTrue(self.invoice_in.payable_move_line_ids)
