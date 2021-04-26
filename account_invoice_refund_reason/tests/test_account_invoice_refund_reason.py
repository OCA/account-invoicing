# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.tests.common import SavepointCase


class TestAccountMoveRefundReason(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Prepare a bunch of useful records to be used in invoice generation
        account_type = cls.env.ref("account.data_account_type_revenue")
        account = cls.env["account.account"].search(
            [("user_type_id", "=", account_type.id)], limit=1
        )
        journal = cls.env["account.journal"].search([("type", "=", "sale")], limit=1)
        partner = cls.env.ref("base.res_partner_3")
        payment_term = cls.env.ref("account.account_payment_term_advance")
        product = cls.env.ref("product.product_product_5")

        # Prepare proper records:
        # 1- return reason
        cls.reason = cls.env.ref(
            "account_invoice_refund_reason.refund_reason_cancellation"
        )
        # 2- customer invoice (needs to be posted)
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "invoice_payment_term_id": payment_term.id,
                "journal_id": journal.id,
                "partner_id": partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "quantity": 10.0,
                            "account_id": account.id,
                            "name": "product test 5",
                            "price_unit": 100.00,
                        },
                    )
                ],
            }
        )
        cls.invoice.action_post()
        # 3- refund wizard
        refund_wizard_obj = cls.env["account.move.reversal"].with_context(
            # Let the `default_get` retrieve the invoice from context
            active_model="account.move",
            active_ids=cls.invoice.ids,
        )
        cls.refund_wizard = refund_wizard_obj.create(
            {
                "reason": "no reason",
                "date": datetime.date.today() + datetime.timedelta(days=1),
                "refund_method": "refund",
            }
        )

    def _play_reason_onchange(self):
        self.refund_wizard.reason_id = self.reason
        self.refund_wizard._onchange_reason_id()

    def test_00_onchange_reason_id(self):
        """Checks that the wizard reason description changes when the reason
        is changed"""
        self._play_reason_onchange()
        self.assertEqual(self.refund_wizard.reason, self.reason.name)

    def test_01_wizard_invoice_refund(self):
        """Checks that the reversed move has the correct reason linked to it"""
        self._play_reason_onchange()
        self.refund_wizard.reverse_moves()
        self.assertEqual(self.invoice.reason_id.id, self.reason.id)
