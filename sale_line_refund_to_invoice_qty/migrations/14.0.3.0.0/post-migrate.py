from openupgradelib import openupgrade

# pylint: disable=W7950
from odoo.addons.sale_line_refund_to_invoice_qty.hooks import post_init_hook


@openupgrade.migrate()
def migrate(env, version):
    post_init_hook(env.cr, env)
