# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api, tools


def pre_init_hook(cr):
    if not tools.config.options.get("without_demo", False):
        env = api.Environment(cr, SUPERUSER_ID, {})
        modules = env["ir.module.module"].search(
            [
                ("name", "in", ["purchase_stock", "sale_stock"]),
                ("state", "!=", "installed"),
            ]
        )
        modules_dep = modules.upstream_dependencies(
            exclude_states=('installed', 'uninstallable', 'to remove'))
        (modules_dep+modules).write({"state": "to install"})
