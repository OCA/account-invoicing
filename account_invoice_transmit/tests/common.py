# Copyright 2020 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class AccountInvoicePrintCommon(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        """
        Create 5 partners with 2 invoices by partner.

        Only partner 0 and 2 should received invoice by letter
        """
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, force_report_rendering=True
            )
        )

        cls.AccountAccount = cls.env["account.account"]
        cls.AccountMove = cls.env["account.move"]
        cls.AccountMoveLine = cls.env["account.move.line"]
        cls.AccountInvoicePrint = cls.env["account.invoice.print"]
        cls.AccountJournal = cls.env["account.journal"]
        cls.email = cls.env.ref("account_invoice_transmit_method.mail")
        cls.post = cls.env.ref("account_invoice_transmit_method.post")

        for i in range(5):
            partner = cls.env["res.partner"].create(
                {
                    "name": "TEST {i}",
                    "ref": "{i}",
                }
            )
            setattr(cls, f"partner_{i}", partner)
        # partner 0 and 2 receive invoice by post
        cls.partner_0.customer_invoice_transmit_method_id = cls.post
        cls.partner_2.customer_invoice_transmit_method_id = cls.post
        # partner 1 and 3 receive invoice by email but only 1 has an email
        cls.partner_1.customer_invoice_transmit_method_id = cls.email
        cls.partner_1.email = "t@dummy.com"
        cls.partner_3.customer_invoice_transmit_method_id = cls.email
        # partner 4 has not transmit method defined

        cls.company = cls.env.ref("base.main_company")
        cls.account_recv = cls.company_data["default_account_receivable"]
        cls.account_payable = cls.company_data["default_account_payable"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.journal = cls.company_data["default_journal_sale"]
        cls.product = cls.env.ref("product.product_product_4")

        # create 2 invoices for each partner
        cls.invoices = cls.AccountMove.browse()
        for i in range(2):
            for p in range(5):
                partner = getattr(cls, f"partner_{p}")
                # Instance: invoice
                invoice = cls.AccountMove.create(
                    {
                        "partner_id": partner.id,
                        "move_type": "out_invoice",
                        "invoice_date": "2019-01-21",
                        "date": "2019-01-21",
                        "invoice_line_ids": [
                            Command.create(
                                {
                                    "name": f"test {i} {p}",
                                    "price_unit": 100.00 * p * i,
                                    "quantity": 1,
                                    "product_id": cls.product.id,
                                }
                            )
                        ],
                    }
                )
                setattr(cls, f"partner_{p}_invoice_{i}", invoice)
                cls.invoices |= invoice
        cls.invoices.action_post()

    def filter(self, record):
        # required to mute logger
        return 0

    def _print_invoices(self, invoices):
        invoice_print = self.AccountInvoicePrint.create(
            {"invoice_ids": [(6, 0, invoices.ids)]}
        )
        return invoice_print.generate_report()

    def _sort_invoices(self, invoices):
        return invoices.sorted(
            lambda i: (i.partner_id.name and i.partner_id.name.lower(), i.name)
        )

    def _get_invoice_ids_from_invoices_path(self, invoices_path):
        return [int(p.split(".")[1]) for p in invoices_path]

    def _generate_invoice_document(self, invoice):
        self.env["ir.actions.report"]._render_qweb_pdf(
            "account.report_invoice", res_ids=invoice.ids
        )

    def assertAttachmentCount(self, instances, count):
        attachment_count = self.env["ir.attachment"].search_count(
            [("res_id", "in", instances.ids), ("res_model", "=", instances._name)]
        )
        self.assertEqual(count, attachment_count)
