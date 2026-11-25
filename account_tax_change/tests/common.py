# Copyright 2023 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests.common import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class AccountTaxChangeCommon(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Prepare the taxes and products
        cls.product_b.taxes_id -= cls.product_a.taxes_id
        # Set a different tax amount to ensure invoice totals are well recomputed
        cls.product_a.taxes_id.amount /= 2
        # Prepare invoices
        cls.invoice_tax_a = cls.init_invoice("out_invoice", products=cls.product_a)
        cls.invoice_tax_b = cls.init_invoice("out_invoice", products=cls.product_b)
        # Configure the tax change
        cls.tax_change_a2b = cls.env["account.tax.change"].create(
            {
                "name": "TEST A2B",
                "date": cls.invoice_tax_a.invoice_date,
                "change_line_ids": [
                    (
                        0,
                        0,
                        {
                            "tax_src_id": cls.tax_sale_a.id,
                            "tax_dest_id": cls.tax_sale_b.id,
                        },
                    ),
                ],
            }
        )

    @classmethod
    def apply_tax_change(cls, tax_change, invoices):
        with Form(cls.env["account.move.apply.tax.change"]) as wiz_form:
            wiz_form.tax_change_id = tax_change
            for invoice in invoices:
                wiz_form.invoice_ids.add(invoice)
            wiz = wiz_form.save()
            wiz.validate()
