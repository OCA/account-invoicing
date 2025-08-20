from odoo.tests.common import Form, TransactionCase


class TestAccountInvoiceLineSequence(TransactionCase):
    def test_account_invoice_line_sequence(self):
        invoice = self.env.ref("account.1_demo_invoice_1")
        invoice.button_draft()
        max_sequence = max(invoice.invoice_line_ids.mapped("sequence2"))
        with Form(invoice) as form:
            with form.invoice_line_ids.new() as line:
                line.name = "test"
                line.product_id = invoice.invoice_line_ids[0].product_id
            with form.invoice_line_ids.edit(len(form.invoice_line_ids) - 1) as line:
                self.assertEqual(line.sequence2, max_sequence + 1)
        self.assertEqual(invoice.invoice_line_ids[-1].sequence2, max_sequence + 1)
        line_data = invoice.invoice_line_ids[-1].copy_data()[0]
        invoice.write(
            {
                "invoice_line_ids": [(0, 0, line_data)],
            }
        )
        self.assertEqual(invoice.invoice_line_ids[-1].sequence2, max_sequence + 2)

    def test_single_invoice_creation_using_form(self):
        """Added new test case for create method"""
        partner = self.env.ref("base.res_partner_1")
        product = self.env.ref("product.product_product_1")
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        ) as form:
            form.partner_id = partner
            with form.invoice_line_ids.new() as line:
                line.name = "Test Product"
                line.product_id = product
                line.quantity = 1
                line.price_unit = 100.0
        new_invoice = form.save()
        self.assertEqual(
            new_invoice.invoice_line_ids[:1].sequence2, 1, "Sequence2 is not 1"
        )
