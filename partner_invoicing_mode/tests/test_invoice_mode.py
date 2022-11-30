# Copyright 2022 Opener B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestInvoiceModeAtShipping(TransactionCase):
    def test_invoice_job_related_action(self):
        """Dedicated invoice view is present in queue job's multi invoice action"""
        invoice1 = self.env.ref("account.1_demo_invoice_1").copy()
        invoice2 = self.env.ref("account.1_demo_invoice_1").copy()
        job_single = self.env["queue.job"].search(
            [("uuid", "=", invoice1.with_delay()._validate_invoice().uuid)]
        )
        action_single = job_single.open_related_action()
        self.assertFalse(action_single.get("view_id"))
        job_multi = self.env["queue.job"].search(
            [("uuid", "=", (invoice1 + invoice2).with_delay()._validate_invoice().uuid)]
        )
        action_multi = job_multi.open_related_action()
        self.assertEqual(
            action_multi["view_id"], self.env.ref("account.view_out_invoice_tree").id
        )
