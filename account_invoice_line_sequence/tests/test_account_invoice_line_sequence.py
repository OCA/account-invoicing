from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestAccountInvoiceLineSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_account_invoice_line_sequence(self):
        invoice = self.env.ref("account.1_demo_invoice_1")
        invoice.button_draft()

        invoice_line = invoice.invoice_line_ids.filtered(
            lambda line: line.display_type not in ("line_section", "line_note")
        )[0]
        max_sequence = max(invoice.invoice_line_ids.mapped("sequence2"))

        with Form(invoice) as form:
            with form.invoice_line_ids.new() as line:
                line.product_id = invoice_line.product_id
                line.name = "test"
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
