# Copyright 2021 Eder Brito - pingotecnologia.com.br

from odoo.tests import common


class TestAccountInvoiceInstallment(common.TransactionCase):
    def create_in_invoice(self):
        account200 = self.env["account.account"].create(
            {
                "code": "200",
                "name": "Account 200",
                "user_type_id": self.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        partner_id = self.env.ref("base.res_partner_12").id
        move_vals = {
            "move_type": "in_invoice",
            "partner_id": partner_id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Test product",
                        "quantity": 1,
                        "price_unit": 450,
                        "account_id": account200.id,
                    },
                )
            ],
        }
        in_invoice = (
            self.env["account.move"]
            .with_context(default_move_type="in_invoice")
            .create(move_vals)
        )
        return in_invoice

    def create_out_invoice(self):
        account100 = self.env["account.account"].create(
            {
                "code": "100",
                "name": "Account 100",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        partner_id = self.env.ref("base.res_partner_12").id
        move_vals = {
            "move_type": "in_invoice",
            "partner_id": partner_id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Test product",
                        "quantity": 1,
                        "price_unit": 450,
                        "account_id": account100.id,
                    },
                )
            ],
        }
        out_invoice = (
            self.env["account.move"]
            .with_context(default_move_type="out_invoice")
            .create(move_vals)
        )
        return out_invoice

    def test_compute(self):
        in_invoice = self.create_in_invoice()
        out_invoice = self.create_out_invoice()

        out_invoice._compute_receivable_move_line_ids()
        in_invoice._compute_payable_move_line_ids()

        self.isAssert(out_invoice.receivable_move_line_ids)
        self.isAssert(in_invoice.payable_move_line_ids)
