# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import SavepointCase


class AccountTaxChangeCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(AccountTaxChangeCommon, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Prepare the taxes and products
        cls.tax_sale_a = cls.env["account.tax"].create(
            {
                "name": "Tax 7.5",
                "amount": 7.5,
                "amount_type": "percent",
                "type_tax_use": "sale",
            }
        )
        cls.tax_sale_b = cls.env["account.tax"].create(
            {
                "name": "Tax 15.0",
                "amount": 15.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
            }
        )
        cls.product_a = cls.env.ref("product.product_product_1")
        cls.product_a.taxes_id = cls.tax_sale_a
        cls.product_b = cls.env.ref("product.product_product_2")
        cls.product_b.taxes_id = cls.tax_sale_b
        # Prepare invoices
        cls.invoice_tax_a = cls.init_invoice("out_invoice", products=cls.product_a)
        cls.invoice_tax_b = cls.init_invoice("out_invoice", products=cls.product_b)
        # Configure the tax change
        cls.tax_change_a2b = cls.env["account.tax.change"].create(
            {
                "name": "TEST A2B",
                "date": cls.invoice_tax_a.date_invoice,
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
    def init_invoice(cls, type_, products):
        partner = cls.env.ref("base.res_partner_3")
        payment_term = cls.env.ref("account.account_payment_term_advance")
        journal = cls.env["account.journal"].search(
            [("type", "=", "sale")],
            limit=1
        )
        account = cls.env["account.account"].search(
            [
                ("user_type_id", "=",
                 cls.env.ref("account.data_account_type_revenue").id)
            ],
            limit=1
        )
        invoice_line_data = []
        for product in products:
            invoice_line_data.append(
                (
                    0, 0,
                    {
                        "product_id": product.id,
                        "quantity": 1.0,
                        "account_id": account.id,
                        "name": "product test 1",
                        "price_unit": 1000,
                        "invoice_line_tax_ids": [(6, 0, product.taxes_id.ids)],
                    }
                )
            )
        return cls.env["account.invoice"].create(
            dict(
                type=type_,
                name="Test Customer Invoice",
                reference_type="none",
                payment_term_id=payment_term.id,
                journal_id=journal.id,
                partner_id=partner.id,
                invoice_line_ids=invoice_line_data,
                date_invoice="2019-01-01",
                date="2019-01-01",
            )
        )

    @classmethod
    def apply_tax_change(cls, tax_change, invoices):
        wiz_model = cls.env["account.move.apply.tax.change"]
        wiz_vals = wiz_model.with_context(
            active_model="account.invoice",
            active_ids=invoices.ids,
        ).default_get(["company_id", "invoice_ids"])
        wiz_vals["tax_change_id"] = tax_change.id
        wiz = wiz_model.create(wiz_vals)
        wiz.validate()
