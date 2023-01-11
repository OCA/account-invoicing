# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from openupgradelib import openupgrade

_field_spec = [
    (
        "can_self_invoice",
        "account.move",
        "account_move",
        "boolean",
        False,
        "account_invoice_supplier_self_invoice",
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _field_spec)
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET can_self_invoice = TRUE
        FROM res_partner rp
        WHERE rp.id = am.commercial_partner_id AND rp.self_invoice
    """,
    )
