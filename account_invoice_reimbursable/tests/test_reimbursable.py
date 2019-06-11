from odoo.tests.common import TransactionCase
from odoo import fields


class TestReimbursable(TransactionCase):
    def setUp(self):
        super().setUp()
        self.currency_eur = self.env.ref('base.EUR')
        self.currency_usd = self.env.ref('base.USD')
        self.main_company = self.env.ref('base.main_company')
        self.env.cr.execute(
            """UPDATE res_company SET currency_id = %s
            WHERE id = %s""",
            (self.main_company.id, self.currency_eur.id),
        )
        self.journal = self.env['account.journal'].create({
            'name': 'Journal',
            'type': 'purchase',
            'code': 'TEST',
        })
        self.partner = self.env['res.partner'].create({
            'supplier': True,
            'name': 'Partner',
        })
        self.reimbursable_partner = self.env['res.partner'].create({
            'supplier': True,
            'name': 'Reimbursable Partner',
        })
        self.product = self.env['product.product'].create({
            'name': 'Product',
        })
        self.reimbursable = self.env['product.product'].create({
            'name': 'Reimbursable',
            'type': 'service',
        })

    def create_invoice_vals(self):
        return {
            'partner_id': self.partner.id,
            'account_id': self.partner.property_account_payable_id.id,
            'journal_id': self.journal.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'account_id':
                    self.product.product_tmpl_id.get_product_accounts(

                    )['expense'].id,
                'name': self.product.name,
                'price_unit': 100,
            })]
        }

    def test_none(self):
        invoice = self.complete_check_invoice(0)
        invoice.action_invoice_open()
        move = invoice.move_id
        lines = move.line_ids.filtered(
            lambda r: r.partner_id == self.reimbursable_partner)
        self.assertFalse(lines)

    def test_simple(self):
        invoice = self.complete_check_invoice(100)
        invoice.action_invoice_open()
        move = invoice.move_id
        lines = move.line_ids.filtered(
            lambda r: r.partner_id == self.reimbursable_partner)
        self.assertTrue(lines)
        self.assertEqual(100, sum(lines.mapped('debit')))
        self.assertEqual(200, invoice.executable_total)

    def test_grouped(self):
        self.journal.group_invoice_lines = True
        invoice = self.complete_check_invoice(100)
        invoice.action_invoice_open()
        move = invoice.move_id
        lines = move.line_ids.filtered(
            lambda r: r.partner_id == self.reimbursable_partner)
        self.assertTrue(lines)
        self.assertEqual(100, sum(lines.mapped('debit')))
        self.assertEqual(200, invoice.executable_total)

    def test_refund(self):
        invoice = self.complete_check_invoice(100)
        invoice.action_invoice_open()
        refund_action = self.env['account.invoice.refund'].with_context(
            active_ids=invoice.ids
        ).create({
            'description': 'Testing'
        }).invoice_refund()
        self.assertTrue(refund_action['domain'])
        refund = self.env['account.invoice'].search(refund_action['domain'])
        self.assertEqual(len(refund), 1)
        self.assertTrue(refund.reimbursable_ids)
        self.assertEqual(refund.amount_total, 100)
        self.assertEqual(refund.reimbursable_count, 1)
        self.assertEqual(refund.executable_total, 200)

    def test_currency(self):
        invoice = self.complete_check_invoice(60)
        invoice.write({'currency_id': self.currency_usd.id})
        # Invoice amount 100 usd reimburs 60 usd
        invoice.action_invoice_open()
        currency = invoice.currency_id._convert(
            invoice.amount_total, self.currency_eur,
            invoice.company_id, fields.Date.today())
        self.assertEqual(invoice.amount_total_company_signed, currency)

    def complete_check_invoice(self, amount):
        invoice = self.env['account.invoice'].with_context(
            default_type='in_invoice', type='in_invoice',
            journal_type='purchase'
        ).create(self.create_invoice_vals())
        self.assertEqual(invoice.amount_total, 100)
        self.assertEqual(invoice.reimbursable_count, 0)
        self.assertEqual(invoice.executable_total, 100)
        reimbursable = self.env['account.invoice.reimbursable'].new({
            'invoice_id': invoice.id,
            'amount': amount
        })
        reimbursable.partner_id = self.reimbursable_partner
        self.assertFalse(reimbursable.account_id)
        reimbursable._onchange_partner_id()
        self.assertTrue(reimbursable.account_id)
        reimbursable.product_id = self.reimbursable
        self.assertFalse(reimbursable.name)
        reimbursable._onchange_product_id()
        self.assertTrue(reimbursable.name)
        reimbursable = reimbursable.create(reimbursable._convert_to_write(
            reimbursable._cache))
        self.assertTrue(reimbursable.description)
        invoice.refresh()
        self.assertEqual(invoice.amount_total, 100)
        self.assertEqual(invoice.reimbursable_count, 1)
        self.assertEqual(invoice.executable_total, 100 + amount)
        return invoice
