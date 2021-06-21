from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET alternate_payer_id = ai.alternate_payer_id
        FROM account_invoice ai
        WHERE ai.alternate_payer_id IS NOT NULL
            AND ai.id = am.old_invoice_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET partner_id = am.alternate_payer_id
        FROM
            account_move am,
            account_account as aa,
            account_account_type as aat
        WHERE am.alternate_payer_id IS NOT NULL
            AND am.id = aml.move_id
            AND am.state = 'draft'
            AND aat.type in ('receivable', 'payable')
            AND aa.id = aml.account_id
            AND aat.id = aa.user_type_id
        """,
    )
