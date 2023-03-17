# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE wizard_update_invoice_supplierinfo
        DROP CONSTRAINT IF EXISTS wizard_update_invoice_supplierinfo_invoice_id_fkey
        """,
    )
    # Prevent having records that weren't vacuumed as they could provoke a key error
    # for the new constraint
    openupgrade.logged_query(
        env.cr, "TRUNCATE wizard_update_invoice_supplierinfo CASCADE"
    )
