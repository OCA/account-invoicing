#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import tests


class TestGroupTaxAmount (tests.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tax_model = cls.env['account.tax']

        # Original group tax with percents 8.8 and 13.2
        original_first_part_tax_form = tests.Form(tax_model)
        original_first_part_tax_form.name = "Test original first tax"
        original_first_part_tax_form.amount_type = 'percent'
        original_first_part_tax_form.amount = 8.8
        cls.original_first_part_tax = original_first_part_tax_form.save()

        original_second_part_tax_form = tests.Form(tax_model)
        original_second_part_tax_form.name = "Test original second tax"
        original_second_part_tax_form.amount_type = 'percent'
        original_second_part_tax_form.amount = 13.2
        cls.original_second_part_tax = original_second_part_tax_form.save()

        original_group_tax_form = tests.Form(tax_model)
        original_group_tax_form.name = "Test original group tax"
        original_group_tax_form.amount_type = 'group'
        original_group_tax_form.children_tax_ids.add(cls.original_first_part_tax)
        original_group_tax_form.children_tax_ids.add(cls.original_second_part_tax)
        cls.original_group_tax = original_group_tax_form.save()

        # New group tax with percents 8.8 and 13.2,
        # note that the second tax is of type 'last_percent'
        new_first_part_tax_form = tests.Form(tax_model)
        new_first_part_tax_form.name = "Test new first tax"
        new_first_part_tax_form.amount_type = 'percent'
        new_first_part_tax_form.amount = 8.8
        cls.new_first_part_tax = new_first_part_tax_form.save()

        new_second_part_tax_form = tests.Form(tax_model)
        new_second_part_tax_form.name = "Test new second tax"
        new_second_part_tax_form.amount_type = 'last_percent'
        new_second_part_tax_form.amount = 13.2
        cls.new_second_part_tax = new_second_part_tax_form.save()

        new_group_tax_form = tests.Form(tax_model)
        new_group_tax_form.name = "Test new group tax"
        new_group_tax_form.amount_type = 'group'
        new_group_tax_form.children_tax_ids.add(cls.new_first_part_tax)
        new_group_tax_form.children_tax_ids.add(cls.new_second_part_tax)
        cls.new_group_tax = new_group_tax_form.save()

        # Create a 22 percent tax and an invoice with only that tax,
        # the invoice will be used to check other invoices' amounts
        percent_group_tax_form = tests.Form(tax_model)
        percent_group_tax_form.name = "Test percent group tax"
        percent_group_tax_form.amount_type = 'percent'
        percent_group_tax_form.amount = 22
        cls.percent_group_tax = percent_group_tax_form.save()

        percent_group_invoice_form = tests.Form(cls.env['account.invoice'])
        percent_group_invoice_form.partner_id = cls.env.ref('base.res_partner_1')
        with percent_group_invoice_form.invoice_line_ids.new() as line:
            line.name = "Test invoice line"
            line.quantity = 1
            line.price_unit = 241.56
            line.invoice_line_tax_ids.clear()
            line.invoice_line_tax_ids.add(cls.percent_group_tax)
        cls.percent_group_invoice = percent_group_invoice_form.save()

    def test_original_group_percent(self):
        """
        Check that a group tax having children with 8.8% and 13.2%
        does not have the same tax amount of a tax having 22%.

        This test simply shows that Odoo standard calculation is broken
        for this particular edge case.
        """
        invoice_form = tests.Form(self.env['account.invoice'])
        invoice_form.partner_id = self.env.ref('base.res_partner_1')
        with invoice_form.invoice_line_ids.new() as line:
            line.name = "Test invoice line"
            line.quantity = 1
            line.price_unit = 241.56
            line.invoice_line_tax_ids.clear()
            line.invoice_line_tax_ids.add(self.original_group_tax)
        invoice = invoice_form.save()

        self.assertNotEqual(
            invoice.amount_total,
            self.percent_group_invoice.amount_total,
            "Odoo is correctly computing the invoice total",
        )
        self.assertNotEqual(
            self.percent_group_invoice.tax_line_ids.mapped('amount')[0],
            sum(invoice.tax_line_ids.mapped('amount')),
            "Odoo is correctly computing the grouped tax amount",
        )

    def test_new_group_percent(self):
        """
        Check that a group tax having children with 8.8% and 13.2%
        has the same tax amount of a tax having 22%.

        This test uses the new `last_percent` amount type for the second tax.
        """
        invoice_form = tests.Form(self.env['account.invoice'])
        invoice_form.partner_id = self.env.ref('base.res_partner_1')
        with invoice_form.invoice_line_ids.new() as line:
            line.name = "Test invoice line"
            line.quantity = 1
            line.price_unit = 241.56
            line.invoice_line_tax_ids.clear()
            line.invoice_line_tax_ids.add(self.new_group_tax)
        invoice = invoice_form.save()

        self.assertEqual(
            invoice.amount_total,
            self.percent_group_invoice.amount_total,
            "This module is not correctly computing the invoice total",
        )
        self.assertEqual(
            self.percent_group_invoice.tax_line_ids.mapped('amount')[0],
            sum(invoice.tax_line_ids.mapped('amount')),
            "This module is not correctly computing the grouped tax amount",
        )
        self.assertCountEqual(
            invoice.tax_line_ids.mapped('amount'),
            [21.26, 31.88],
            "This module is not correctly computing the tax amounts",
        )
