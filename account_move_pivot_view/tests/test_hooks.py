# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from .. import uninstall_hook


@tagged("post_install", "-at_install")
class TestUninstallHook(TransactionCase):
    def test_uninstall_hook(self):
        self.env.ref("account.action_move_in_invoice").unlink()

        actions_to_restore = [
            "account.action_move_in_invoice",
            "account.action_move_in_refund_type",
            "account.action_move_in_receipt_type",
            "account.action_move_out_invoice",
            "account.action_move_out_refund_type",
            "account.action_move_out_receipt_type",
        ]

        for xml_id in actions_to_restore:
            action = self.env.ref(xml_id, raise_if_not_found=False)
            if action:
                self.assertIn("pivot", action.view_mode)

        uninstall_hook(self.env)

        for xml_id in actions_to_restore:
            action = self.env.ref(xml_id, raise_if_not_found=False)
            if action:
                self.assertEqual(action.view_mode, "list,kanban,form,activity")
