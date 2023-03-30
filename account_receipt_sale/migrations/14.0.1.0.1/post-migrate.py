#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.addons.account_receipt_sale import invert_receipt_refund_quantity


@openupgrade.migrate()
def migrate(env, version):
    invert_receipt_refund_quantity(env)
