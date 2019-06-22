from odoo.tests.common import TransactionCase


class TestInvoiceBaseTaxZero(TransactionCase):
    def setUp(self):
        super().setUp()
        self.journal = self.env['account.journal'].create({
            'name': 'Journal',
            'type': 'purchase',
            'code': 'TEST',
        })
        self.partner = self.env['res.partner'].create({
            'supplier': True,
            'name': 'Partner',
        })
        self.product = self.env['product.product'].create({
            'name': 'Product',
        })
        self.account_type = self.env['account.account.type'].create({
            'name': 'Test',
            'type': 'other',
        })
        self.account_vat = self.env['account.account'].create({
            'name': 'VAT account Credit',
            'code': 'VatCredit',
            'user_type_id': self.account_type.id,
            'reconcile': True,
        })
        self.tax22 = self.env['account.tax'].create({
            'name': 'TAX 22%',
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'amount': 22.0,
            'account_id': self.account_vat.id,
            'refund_account_id': self.account_vat.id,
        })
        self.tax10 = self.env['account.tax'].create({
            'name': 'TAX 10%',
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'amount': 10.0,
            'account_id': self.account_vat.id,
            'refund_account_id': self.account_vat.id,
        })

    def create_invoice_vals(self):
        return {
            'partner_id': self.partner.id,
            'account_id': self.partner.property_account_payable_id.id,
            'journal_id': self.journal.id,
            }

    def test_01_invoice_one_tax_zero(self):
        """ Tests invoice with one tax with amount zero"""
        vals = self.create_invoice_vals()
        invoice = self.env['account.invoice'].create(vals)
        line1_val = {
            'invoice_id': invoice.id,
            'product_id': self.product.id,
            'account_id':
                self.product.product_tmpl_id.get_product_accounts(
                )['expense'].id,
            'name': self.product.name,
            'price_unit': 100,
            'invoice_line_tax_ids': [(6, 0, [self.tax22.id])],
            }
        self.env['account.invoice.line'].create(line1_val)
        line2_val = {
            'invoice_id': invoice.id,
            'product_id': self.product.id,
            'account_id':
                self.product.product_tmpl_id.get_product_accounts(
                )['expense'].id,
            'name': self.product.name,
            'price_unit': -100,
            'invoice_line_tax_ids': [(6, 0, [self.tax22.id])],
            }
        self.env['account.invoice.line'].create(line2_val)
        invoice.compute_taxes()
        invoice.action_invoice_open()
        aml = invoice.move_id.line_ids.filtered(
            lambda r: r.tax_line_id == self.tax22)

        self.assertEqual(len(aml), 1)
        self.assertEqual(aml.balance, 0)

    def test_02_invoice_two_taxes_one_tax_zero(self):
        """ Tests invoice with two taxes with one tax amount zero"""
        vals = self.create_invoice_vals()
        invoice = self.env['account.invoice'].create(vals)
        line1_val = {
            'invoice_id': invoice.id,
            'product_id': self.product.id,
            'account_id':
                self.product.product_tmpl_id.get_product_accounts(
                )['expense'].id,
            'name': self.product.name,
            'price_unit': 100,
            'invoice_line_tax_ids': [(6, 0, [self.tax22.id])],
            }
        self.env['account.invoice.line'].create(line1_val)
        line2_val = {
            'invoice_id': invoice.id,
            'product_id': self.product.id,
            'account_id':
                self.product.product_tmpl_id.get_product_accounts(
                )['expense'].id,
            'name': self.product.name,
            'price_unit': -100,
            'invoice_line_tax_ids': [(6, 0, [self.tax22.id])],
            }
        self.env['account.invoice.line'].create(line2_val)
        line3_val = {
            'invoice_id': invoice.id,
            'product_id': self.product.id,
            'account_id':
                self.product.product_tmpl_id.get_product_accounts(
                )['expense'].id,
            'name': self.product.name,
            'price_unit': 100,
            'invoice_line_tax_ids': [(6, 0, [self.tax10.id])],
            }
        self.env['account.invoice.line'].create(line3_val)
        invoice.compute_taxes()
        invoice.action_invoice_open()
        aml22 = invoice.move_id.line_ids.filtered(
            lambda r: r.tax_line_id == self.tax22)
        aml10 = invoice.move_id.line_ids.filtered(
            lambda r: r.tax_line_id == self.tax10)

        self.assertEqual(len(aml22), 1)
        self.assertEqual(len(aml10), 1)
        self.assertEqual(aml10.balance, -10)

        self.assertEqual(aml22.balance, 0)
