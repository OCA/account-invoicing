# -*- coding: utf-8 -*-
# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase


class TestOverdueWarn(TransactionCase):
    def setUp(self):
        super(TestOverdueWarn, self).setUp()
        self.company = self.env.ref("base.main_company")
        self.bad_payer = self.env["res.partner"].create(
            {
                "name": "Bad payer",
                "country_id": self.env.ref("base.fr").id,
                "company_id": self.company.id,
            }
        )
        today = datetime.now().date()
        revenue_acc = self.env["account.account"].search(
            [
                ("company_id", "=", self.company.id),
                (
                    "user_type",
                    "=",
                    self.env.ref("account.data_account_type_income").id,
                ),
            ],
            limit=1,
        )
        self.out_invoice1 = self.env["account.invoice"].create(
            {
                "partner_id": self.bad_payer.id,
                "type": "out_invoice",
                "company_id": self.company.id,
                "currency_id": self.company.currency_id.id,
                "date_invoice": today - timedelta(days=5),
                "date_due": today - timedelta(days=5),
                "account_id": self.bad_payer.property_account_receivable.id,
                "invoice_line": [
                    (
                        0,
                        0,
                        {
                            "name": "test line",
                            "price_unit": 500,
                            "quantity": 1,
                            "account_id": revenue_acc.id,
                        },
                    )
                ],
            }
        )
        self.out_invoice1.signal_workflow('invoice_open')
        self.out_invoice2 = self.env["account.invoice"].create(
            {
                "partner_id": self.bad_payer.id,
                "type": "out_invoice",
                "company_id": self.company.id,
                "currency_id": self.company.currency_id.id,
                "date_invoice": datetime.now().date(),
                "date_due": today + timedelta(days=30),
                "account_id": self.bad_payer.property_account_receivable.id,
                "invoice_line": [
                    (
                        0,
                        0,
                        {
                            "name": "test line",
                            "price_unit": 1000,
                            "quantity": 1,
                            "account_id": revenue_acc.id,
                        },
                    )
                ],
            }
        )
        self.out_invoice2.signal_workflow('invoice_open')

    def test_overdue_warn(self):
        self.assertEqual(self.bad_payer.overdue_invoice_count, 1)
        self.assertEqual(self.bad_payer.overdue_invoice_amount, 500)
