# Copyright 2026, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestSaleInvoiceAdvanceCompensation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create({"name": "Advance Customer"})

        cls.receivable = cls.env["account.account"].create(
            {
                "name": "Receivable",
                "code": "SACRCV",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.partner.property_account_receivable_id = cls.receivable
        cls.income = cls.env["account.account"].create(
            {
                "name": "Income",
                "code": "SACINC",
                "account_type": "income",
            }
        )
        cls.prepayment = cls.env["account.account"].create(
            {
                "name": "Prepayments",
                "code": "SACADV",
                "account_type": "asset_prepayments",
                "reconcile": True,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Service",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 1000.0,
                "property_account_income_id": cls.income.id,
                "taxes_id": [Command.clear()],
            }
        )
        cls.product.categ_id.property_account_downpayment_categ_id = cls.prepayment
        cls.advance_product = cls.env["product.product"].create(
            {
                "name": "Advance",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 600.0,
                "property_account_income_id": cls.prepayment.id,
                "taxes_id": [Command.clear()],
            }
        )
        cls.advance_journal = cls.env["account.journal"].create(
            {
                "name": "Advance",
                "code": "SAC",
                "type": "sale",
                "is_advance_journal": True,
            }
        )
        cls.company.sale_advance_journal_id = cls.advance_journal
        cls.company.sale_advance_product_id = cls.advance_product
        cls.bank_journal = cls.env["account.journal"].create(
            {
                "name": "Bank",
                "code": "SBNK",
                "type": "bank",
            }
        )
        cls.payment_term = cls.env["account.payment.term"].create(
            {
                "name": "30% Advance",
                "line_ids": [
                    Command.create(
                        {
                            "value": "percent",
                            "value_amount": 30.0,
                            "nb_days": 0,
                            "is_advance": True,
                        }
                    ),
                    Command.create(
                        {
                            "value": "percent",
                            "value_amount": 70.0,
                            "nb_days": 30,
                        }
                    ),
                ],
            }
        )

    def _create_invoice(self, product, amount):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "quantity": 1,
                            "price_unit": amount,
                        }
                    )
                ],
            }
        )
        invoice.action_post()
        return invoice

    def _pay_invoice(self, invoice):
        wizard = (
            self.env["account.payment.register"]
            .with_context(
                active_model="account.move",
                active_ids=invoice.ids,
                active_id=invoice.id,
            )
            .create(
                {
                    "payment_date": fields.Date.today(),
                    "journal_id": self.bank_journal.id,
                }
            )
        )
        wizard._create_payments()
        invoice.invalidate_recordset()
        self.assertEqual(invoice.payment_state, "paid")
        return invoice

    def _create_advance_line(self, amount=600.0):
        invoice = self._pay_invoice(self._create_invoice(self.advance_product, amount))
        return invoice.line_ids.filtered(
            lambda line: line.account_id == self.prepayment
        )

    def _create_sale_order(self, amount=1000.0):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "payment_term_id": self.payment_term.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": amount,
                            "tax_id": [Command.clear()],
                        }
                    )
                ],
            }
        )

    def test_payment_term_advance_lines_create_compensation_and_invoice(self):
        order = self._create_sale_order(1000.0)

        self.assertEqual(len(order.advance_compensation_ids), 1)
        compensation = order.advance_compensation_ids
        self.assertEqual(compensation.payment_term_line_id.value_amount, 30.0)
        self.assertEqual(compensation.amount, 300.0)

        order.action_confirm()
        advance_invoice = compensation.action_create_advance_invoice()

        self.assertEqual(compensation.state, "invoiced")
        self.assertEqual(compensation.advance_invoice_id, advance_invoice)
        self.assertEqual(advance_invoice.amount_total, 300.0)
        self.assertEqual(advance_invoice.journal_id, self.advance_journal)
        self.assertEqual(
            advance_invoice.invoice_line_ids.product_id,
            self.advance_product,
        )
        self.assertFalse(compensation.compensation_move_id)
        self.assertTrue(
            advance_invoice.invoice_line_ids.filtered(
                lambda line: line.account_id == self.prepayment
            )
        )

    def test_advance_invoice_uses_standard_sale_journal_without_advance_journal(self):
        order = self._create_sale_order(1000.0)
        order.advance_journal_id = False
        order.action_confirm()

        advance_invoice = order.advance_compensation_ids.action_create_advance_invoice()

        self.assertEqual(advance_invoice.journal_id.type, "sale")
        self.assertEqual(
            advance_invoice.invoice_line_ids.product_id,
            self.advance_product,
        )

    def test_invoice_posting_applies_paid_payment_term_advance_once(self):
        order = self._create_sale_order(1000.0)
        order.action_confirm()
        compensation = order.advance_compensation_ids
        advance_invoice = compensation.action_create_advance_invoice()
        advance_invoice.action_post()
        advance_line = self._pay_invoice(advance_invoice).line_ids.filtered(
            lambda line: line.account_id == self.prepayment
        )

        invoice = order._create_invoices().filtered(
            lambda move: move != advance_invoice
        )
        invoice.ensure_one()
        invoice.action_post()

        self.assertRecordValues(
            compensation,
            [
                {
                    "state": "applied",
                    "invoice_id": invoice.id,
                    "applied_amount": 300.0,
                }
            ],
        )
        self.assertTrue(compensation.compensation_move_id)
        self.assertTrue(advance_line.reconciled)
        self.assertLess(invoice.amount_residual, invoice.amount_total)

        compensation_move = compensation.compensation_move_id
        invoice._apply_sale_advance_compensations()
        self.assertEqual(compensation.compensation_move_id, compensation_move)

    def test_unlinked_advance_is_not_automatically_compensated(self):
        advance_line = self._create_advance_line(300.0)
        order = self._create_sale_order(1000.0)
        order.action_confirm()

        invoice = order._create_invoices()
        invoice.action_post()

        self.assertFalse(order.advance_compensation_ids.advance_line_id)
        self.assertFalse(order.advance_compensation_ids.compensation_move_id)
        self.assertFalse(advance_line.reconciled)

    def test_regular_invoice_wizard_can_skip_automatic_advance_compensation(self):
        order = self._create_sale_order(1000.0)
        order.action_confirm()
        compensation = order.advance_compensation_ids
        advance_invoice = compensation.action_create_advance_invoice()
        advance_invoice.action_post()
        advance_line = self._pay_invoice(advance_invoice).line_ids.filtered(
            lambda line: line.account_id == self.prepayment
        )

        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_model="sale.order", active_ids=order.ids)
            .create(
                {
                    "advance_payment_method": "delivered",
                    "apply_advance_compensation": False,
                }
            )
        )
        wizard.create_invoices()
        invoice = order.invoice_ids.filtered(lambda move: move != advance_invoice)[:1]
        self.assertTrue(invoice.skip_sale_advance_compensation)
        self.assertFalse(compensation.compensation_move_id)
        invoice.action_post()

        self.assertFalse(compensation.compensation_move_id)
        self.assertFalse(advance_line.reconciled)

    def test_final_invoice_does_not_deduct_downpayment_line_twice(self):
        order = self._create_sale_order(1000.0)
        order.action_confirm()
        advance_invoice = order.advance_compensation_ids.action_create_advance_invoice()
        advance_invoice.action_post()
        self._pay_invoice(advance_invoice)

        invoice = order._create_invoices(final=True)

        self.assertFalse(invoice.invoice_line_ids.filtered("is_downpayment"))
        self.assertEqual(invoice.amount_total, 1000.0)

    def test_sale_order_gets_company_advance_defaults(self):
        self.company.sale_advance_journal_id = self.advance_journal
        self.company.sale_advance_product_id = self.advance_product

        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "payment_term_id": self.payment_term.id,
            }
        )

        self.assertEqual(order.advance_journal_id, self.advance_journal)
        self.assertEqual(order.advance_product_id, self.advance_product)

    def test_confirm_requires_advance_product_for_advance_payment_term(self):
        order = self._create_sale_order(1000.0)
        order.advance_product_id = False
        self.company.sale_advance_product_id = False

        with self.assertRaisesRegex(UserError, "Advance Product"):
            order.action_confirm()

    def test_confirm_without_advance_payment_term_does_not_require_advance_product(
        self,
    ):
        payment_term = self.env["account.payment.term"].create(
            {
                "name": "Regular Net 30",
                "line_ids": [
                    Command.create(
                        {
                            "value": "percent",
                            "value_amount": 100.0,
                            "nb_days": 30,
                        }
                    ),
                ],
            }
        )
        order = self._create_sale_order(1000.0)
        order.payment_term_id = payment_term
        order.advance_product_id = False
        self.company.sale_advance_product_id = False

        order.action_confirm()

        self.assertEqual(order.state, "sale")
