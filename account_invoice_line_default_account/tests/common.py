#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.fields import first
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class DefaultAccountCommon(AccountTestInvoicingCommon):

    _default_move_type = "out_invoice"

    @classmethod
    def _create_invoice(cls, user, partner, product=None):
        account_invoice_model = cls.account_invoice_model
        if user:
            account_invoice_model = account_invoice_model.with_user(user.id)

        invoice_form = Form(account_invoice_model)
        invoice_form.partner_id = partner
        with invoice_form.invoice_line_ids.new() as line:
            if product:
                line.product_id = product
            else:
                # Required for invoice lines
                line.name = "Test line"

        return invoice_form.save()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.account_invoice_model = cls.env["account.move"].with_context(
            default_move_type=cls._default_move_type
        )
        cls.partner = cls.env.ref("base.res_partner_3")
        cls.product = cls.env.ref("product.product_product_5")
        cls.invoice = cls._create_invoice(
            # We use the created user in AccountTestInvoicingCommon
            cls.env.user,
            cls.partner,
        )
        invoice_line = first(cls.invoice.invoice_line_ids)
        cls.default_account = invoice_line.account_id
        cls.partner_account = cls.default_account.search(
            [
                ("id", "!=", cls.default_account.id),
            ],
            limit=1,
        )

        cls.other_income_account = cls.env["account.account"].create(
            {
                "name": "Test Income account",
                "code": "TEST",
                "account_type": "income",
            }
        )
