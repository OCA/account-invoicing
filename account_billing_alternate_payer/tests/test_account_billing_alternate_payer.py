# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountBillingAlternatePayer(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.payer = cls.env["res.partner"].create({"name": "Real Estate Agency"})
        cls.tenant_a = cls.env["res.partner"].create({"name": "Tenant A"})
        cls.tenant_b = cls.env["res.partner"].create({"name": "Tenant B"})

    @classmethod
    def _create_invoice(cls, partner, alternate_payer=False, amount=100.0):
        invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "alternate_payer_id": alternate_payer and alternate_payer.id or False,
                "invoice_date": "2026-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_a.id,
                            "quantity": 1,
                            "price_unit": amount,
                            "tax_ids": False,
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        return invoice

    def _create_billing(self, partner):
        billing = self.env["account.billing"].create(
            {
                "partner_id": partner.id,
                "bill_type": "out_invoice",
                "threshold_date": "2026-12-31",
                "threshold_date_type": "invoice_date",
            }
        )
        billing.compute_lines()
        return billing

    def test_billing_groups_invoices_of_the_alternate_payer(self):
        invoice_a = self._create_invoice(self.tenant_a, self.payer)
        invoice_b = self._create_invoice(self.tenant_b, self.payer)
        billing = self._create_billing(self.payer)
        self.assertEqual(
            billing.billing_line_ids.mapped("move_id"),
            invoice_a | invoice_b,
        )
        self.assertEqual(
            set(billing.billing_line_ids.mapped("move_partner_id")),
            {self.tenant_a, self.tenant_b},
        )

    def test_invoice_with_alternate_payer_is_not_billed_to_its_partner(self):
        self._create_invoice(self.tenant_a, self.payer)
        own_invoice = self._create_invoice(self.tenant_a)
        billing = self._create_billing(self.tenant_a)
        self.assertEqual(billing.billing_line_ids.mapped("move_id"), own_invoice)
