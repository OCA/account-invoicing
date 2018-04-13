# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestMultipleDiscount(common.TransactionCase):

    def setUp(self):
        super(TestMultipleDiscount, self).setUp()

        self.product = self.env.ref('product.service_order_01')
        self.partner = self.env.ref('base.res_partner_1')
        self.journalrec = self.env['account.journal'].create(
            {'name': 'Stock journal', 'type': 'sale', 'code': 'TST01'})
        self.payment_term = self.env.ref(
            'account.account_payment_term_advance')
        account_user_type = self.env.ref(
            'account.data_account_type_receivable')
        self.account_rec1_id = self.env['account.account'].sudo().create(dict(
            code="cust_acc",
            name="customer account",
            user_type_id=account_user_type.id,
            reconcile=True,
        ))

        invoice_line_dict = {
            'name': self.product.name,
            'product_id': self.product.id,
            'quantity': 2,
            'account_id': self.env['account.account'].search(
                [('user_type_id', '=', self.env.ref(
                    'account.data_account_type_revenue').id)
                 ],
                limit=1).id,
            'price_unit': self.product.list_price,
        }

        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'invoice_line_ids': [(0, 0, invoice_line_dict)],
            'name': 'Test Customer Invoice',
            'reference_type': 'none',
            'payment_term_id': self.payment_term.id,
            'journal_id': self.journalrec.id,
            'account_id': self.account_rec1_id.id,
        })

    def test_01_onchange(self):
        self.invoice.invoice_line_ids[0].write(
            {'multiple_discount': '+10 + 15,5 -5.5'})
        self.assertEqual(self.invoice.invoice_line_ids[0].discount, 19.77)
        self.assertEqual(
            self.invoice.invoice_line_ids[0].multiple_discount, '10+15.5-5.5')

        self.invoice.invoice_line_ids[0].write({'multiple_discount': None})
        self.assertEqual(self.invoice.invoice_line_ids[0].discount, 0.0)

        with self.assertRaises(ValidationError):
            self.invoice.invoice_line_ids[0].write(
                {'multiple_discount': '10 + 15,5a'})
