# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import SavepointCase
from odoo import exceptions


class TestAccountInvoice(SavepointCase):
    """
    Tests for account.invoice
    """

    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        self.invoice_obj = self.env['account.invoice']
        self.account_obj = self.env['account.account']
        self.partner = self.env.ref('base.res_partner_2')
        self.product = self.env.ref("product.product_product_9")
        acc_revenue = self.env.ref("account.data_account_type_revenue")
        self.account = self.account_obj.create({
            'code': 'ABCDXX',
            'name': 'A random account',
            'user_type_id': acc_revenue.id,
            'reconcile': True,
        })

    def _create_invoice(self, amount, invoice_type="out_invoice"):
        """
        Create an invoice/refund (depending on given invoice_type) with a
        product unit price with the given amount.
        :param amount: float
        :param invoice_type: str
        :return: account.invoice recordset
        """
        invoice_values = {
            'partner_id': self.partner.id,
            'type': invoice_type,
            'invoice_line_ids': [
                (0, False, {
                    'product_id': self.product.id,
                    'name': self.product.name,
                    'price_unit': amount,
                    'account_id': self.account.id,
                    'quantity': 1,
                }),
            ]
        }
        return self.invoice_obj.create(invoice_values)

    def test_invoice_validation_positive(self):
        """
        Ensure the validation of positive invoices still possible.
        :return:
        """
        amounts = [0, 0.1, 1, 10, 1234.56]
        for amount in amounts:
            out_invoice = self._create_invoice(amount=amount)
            out_invoice.action_invoice_open()
            # Do the same for a refund
            out_refund = self._create_invoice(
                amount=amount, invoice_type="out_refund")
            out_refund.action_invoice_open()
            # Now a "in" types
            in_invoice = self._create_invoice(
                amount=amount, invoice_type="in_invoice")
            in_invoice.action_invoice_open()
            in_refund = self._create_invoice(
                amount=amount, invoice_type="in_refund")
            in_refund.action_invoice_open()
        return

    def test_invoice_validation_negative(self):
        """
        Ensure an exception is raised if a user try to validate a
        negative invoice/refund.
        But validation of "in" types should still possible.
        :return:
        """
        amounts = [-0.1, -10, -1234.56]
        for amount in amounts:
            out_invoice = self._create_invoice(amount=amount)
            with self.assertRaises(exceptions.ValidationError) as cm:
                out_invoice.action_invoice_open()
            self.assertIn(out_invoice.display_name, cm.exception.name)
            self.assertIn("validate a negative", cm.exception.name)
            # Now try on a refund.
            out_refund = self._create_invoice(
                amount=amount, invoice_type="out_refund")
            with self.assertRaises(exceptions.ValidationError) as cm:
                out_refund.action_invoice_open()
            self.assertIn(out_refund.display_name, cm.exception.name)
            self.assertIn("validate a negative", cm.exception.name)
            # But it should block anything for "in" types
            in_invoice = self._create_invoice(
                amount=amount, invoice_type="in_invoice")
            in_invoice.action_invoice_open()
            in_refund = self._create_invoice(
                amount=amount, invoice_type="in_refund")
            in_refund.action_invoice_open()
        return
