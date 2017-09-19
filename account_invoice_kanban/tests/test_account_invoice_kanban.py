# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestAccountInvoiceKanban(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceKanban, self).setUp()
        self.account_invoice_model = self.env['account.invoice']
        self.account_journal_model = self.env['account.journal']
        self.account_account_model = self.env['account.account']
        self.kanban_stage_model = self.env['base.kanban.stage']
        self.kanban_abstract_model = self.env['base.kanban.abstract']
        self.partner_id = self.env.ref('base.res_partner_12')
        self.product_id = self.env.ref('product.product_product_3')
        self.receivable = self.env.ref('account.data_account_type_receivable')
        self.journal_sale = self.account_journal_model.\
            search([('type', '=', 'sale')])[0].id
        self.account_receivable = self.account_account_model.\
            search([('user_type_id', '=', self.receivable.id)], limit=1).id
        self.type_revenue = self.env.ref('account.data_account_type_revenue')
        self.account_type_revenue = self.account_account_model.\
            search([('user_type_id', '=', self.type_revenue.id)], limit=1).id
        self.model = self.env['ir.model'].\
            search([('name', '=', 'Invoice'),
                    ('model', '=', 'account.invoice')])
        self.test_stage_1 = self.kanban_stage_model.create({
            'name': 'Test Stage 1',
            'res_model_id': self.model.id,
            'fold': True,
        })

        self.invoice = self.account_invoice_model.create({
            'name': "Test Customer Invoice",
            'journal_id': self.journal_sale,
            'partner_id': self.partner_id.id,
            'account_id': self.account_receivable,
            'stage_id': self.test_stage_1.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product_id.id,
                    'quantity': 1.0,
                    'account_id': self.account_type_revenue,
                    'name': '[PCSC234] PC Assemble SC234',
                    'price_unit': 450.00
                    })
            ],
        })

    def test_read_group_stage_ids(self):
        self.assertEqual(
            self.account_invoice_model._read_group_stage_ids(
                self.kanban_stage_model, [], 'id'),
            self.kanban_stage_model.search([], order='id'),
        )

    def test_copy_method(self):
        self.invoice.copy()
