from odoo.tests.common import TransactionCase


class AutoMergeInvoiceTC(TransactionCase):

    def setUp(self):
        super(AutoMergeInvoiceTC, self).setUp()

        receivable_type = self.env.ref('account.data_account_type_receivable')
        revenue_type = self.env.ref('account.data_account_type_revenue')

        self.account_recv = self.env['account.account'].create({
            'code': u'cust_acc', 'name': u'recv account',
            'user_type_id': receivable_type.id,
            'reconcile': True,
        })

        self.account_revenue = self.env['account.account'].create({
            'code': u'rev_acc', 'name': u'revenue account',
            'user_type_id': revenue_type.id,
        })

        self.inv_journal = self.env['account.journal'].create({
            'name': 'INV journal',
            'code': 'INV',
            'company_id': self.env.user.company_id.id,
            'type': 'sale',
            'default_debit_account_id': self.account_recv.id,
        })

        self.partner_1 = self.env.ref('base.res_partner_1')
        self.partner_1.update({
            'invoice_merge_next_date': '2019-05-15',
            'invoice_merge_recurring_rule_type': 'monthly',
            'invoice_merge_recurring_interval': 1,
            'property_account_receivable_id': self.account_recv.id,
        })

        self.partner_2 = self.env.ref('base.res_partner_2')

        self.product = self.env.ref("product.product_product_1")

    def create_invoice(self, partner, date, price_unit=10, **kwargs):
        params = {
            'partner_id': partner.id,
            'currency_id': 1,
            'account_id': self.account_recv.id,
            'type': 'out_invoice',
            'journal_id': self.inv_journal.id,
            'date_invoice': date,
            'auto_merge': True,
            }
        params.update(kwargs)
        invoice = self.env['account.invoice'].create(params)
        self.env['account.invoice.line'].create({
            'name': 'account line',
            'product_id': self.product.id,
            'quantity': 1,
            'price_unit': price_unit,
            'invoice_id': invoice.id,
            'account_id': self.account_revenue.id,
        })
        return invoice
