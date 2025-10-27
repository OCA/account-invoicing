# Copyright 2020 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account_invoice_transmit.tests.common import AccountInvoicePrintCommon


@tagged("post_install", "-at_install")
class SelfBillingTransmitCommon(AccountInvoicePrintCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # partner 0 and 2 receive invoice by post
        cls.partner_0.supplier_invoice_transmit_method_id = cls.post
        cls.partner_2.supplier_invoice_transmit_method_id = cls.post
        # partner 1 and 3 receive invoice by email but only 1 has an email
        cls.partner_1.supplier_invoice_transmit_method_id = cls.email
        cls.partner_1.email = "t@dummy.com"
        cls.partner_3.supplier_invoice_transmit_method_id = cls.email
        # partner 4 has not transmit method defined

        # create 3 invoices for each partner
        cls.invoices = cls.AccountMove.browse()
        for i in range(3):
            for p in range(5):
                partner = getattr(cls, f"partner_{p}")
                # Instance: invoice
                invoice = cls.AccountMove.create(
                    {
                        "partner_id": partner.id,
                        "move_type": "in_invoice",
                        "invoice_date": "2019-01-21",
                        "date": "2019-01-21",
                        "set_self_invoice": True,
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
