# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestInvoiceSupplierReferenceReuse(SavepointCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()

        # Inspired by TestAccountSupplierInvoice
        # https://github.com/odoo/odoo/blob/11.0/addons/account/tests/test_account_supplier_invoice.py

        self.invoice_account = self.env['account.account'].search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_receivable').id
              )], limit=1).id
        self.invoice_line_account = self.env['account.account'].search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_expenses').id
              )], limit=1).id

        self.invoice = self._create_invoice_with_reference(self, 'ABC123')

    def _create_invoice_with_reference(self, reference):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'account_id': self.invoice_account,
            'type': 'in_invoice',
            'reference': reference
        })
        self.env['account.invoice.line'].create({
            'product_id': self.env.ref('product.product_product_4').id,
            'quantity': 1.0,
            'price_unit': 100.0,
            'invoice_id': invoice.id,
            'name': 'product that cost 100',
            'account_id': self.invoice_line_account,
        })
        invoice.action_invoice_open()
        return invoice

    def test_01_reference_reuse(self):
        """ Check that reusing the reference number is possible
        """
        invoice2 = self._create_invoice_with_reference(self.invoice.reference)
        self.assertEqual(invoice2.reference, self.invoice.reference)
