# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade, openupgrade_180


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_180.convert_company_dependent(env, "res.partner", "vendor_currency_id")
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "customer_currency_id"
    )
