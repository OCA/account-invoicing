# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from openerp.exceptions import UserError


class TestAccountAnalyticLineInvoice(TransactionCase):
    def test_account_invoice_analytic_line(self):
        lines = self.env['account.analytic.line'].search([
            ('project_id', '!=', False),
        ])
        # demo data projects don't have partner_id set, and we unset
        # products to provoke an exception
        lines.filtered(lambda x: not x.partner_id).mapped('project_id').write({
            'partner_id': self.env['res.partner'].search([
                ('customer', '=', True),
                ('is_company', '=', True),
            ], limit=1).id,
        })
        lines.write({'product_id': False})
        with self.assertRaises(UserError):
            # breaks because we didn't configure a product
            self.env['account.analytic.line.invoice'].with_context(
                active_ids=lines.ids,
            ).create({}).action_invoice()
        # configure a product
        invoice_product = self.env['product.product'].search(
            [('sale_ok', '=', True)], limit=1,
        )
        self.env['account.config.settings'].create({
            'account_invoice_analytic_line_product_id': invoice_product.id,
        }).execute()
        self.assertEqual(
            self.env['account.config.settings'].create({})
            .account_invoice_analytic_line_product_id,
            invoice_product,
        )
        self.env['account.config.settings'].create({
            'account_invoice_analytic_line_product_id': False,
        }).execute()
        self.assertFalse(
            self.env['account.config.settings'].create({})
            .account_invoice_analytic_line_product_id
        )
        self.env['account.config.settings'].create({
            'account_invoice_analytic_line_product_id': invoice_product.id,
        }).execute()
        self.env['account.config.settings'].create({
            'account_invoice_analytic_line_product_id': invoice_product.id,
        }).execute()
        # create invoices
        action = self.env['account.analytic.line.invoice'].with_context(
            active_ids=lines.ids,
        ).create({}).action_invoice()
        invoices = self.env['account.invoice'].search(action['domain'])
        self.assertTrue(invoices)
        self.assertEqual(
            invoices.mapped('invoice_line_ids.account_analytic_line_ids'),
            lines,
        )
        self.assertEqual(
            sum(invoices.mapped('invoice_line_ids.quantity')),
            sum(lines.mapped('unit_amount')),
        )
