# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def uninstall_hook(env):
    actions_to_restore = [
        "account.action_move_in_invoice",
        "account.action_move_in_refund_type",
        "account.action_move_in_receipt_type",
        "account.action_move_out_invoice",
        "account.action_move_out_refund_type",
        "account.action_move_out_receipt_type",
    ]

    for xml_id in actions_to_restore:
        action = env.ref(xml_id, raise_if_not_found=False)
        if action:
            action.write({"view_mode": "list,kanban,form,activity"})
