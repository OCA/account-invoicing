# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

# pylint: disable=odoo-addons-relative-import
from odoo.addons.partner_invoicing_mode_at_shipping.hooks import (
    _add_one_invoice_per_shipping,
)


@openupgrade.migrate()
def migrate(env, version):
    _add_one_invoice_per_shipping(env)
