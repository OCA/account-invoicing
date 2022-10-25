# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(
        env.cr, [("account_invoice_refund_reason", "account_move_refund_reason")]
    )
    openupgrade.rename_models(
        env.cr, [("account.invoice.refund.reason", "account.move.refund.reason")]
    )
