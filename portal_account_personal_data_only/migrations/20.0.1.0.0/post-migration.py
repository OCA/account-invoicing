# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # In 20.0, ir.rule records become ir.access ones, so the core portal rules
    # are recreated active. Archive them again, as the post_init_hook does.
    cr.execute(
        """
        UPDATE ir_access SET active = FALSE
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = 'account'
                AND model = 'ir.access'
                AND name IN (
                    'account_invoice_rule_portal',
                    'account_invoice_line_rule_portal'
                )
        )
        """
    )
