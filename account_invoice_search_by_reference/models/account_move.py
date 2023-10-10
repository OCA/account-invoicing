# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"
    _rec_names_search = ["name", "ref"]

    @api.depends("ref", "name")
    def name_get(self):
        res = []
        for inv in self:
            if inv.ref and inv.name != "/":
                res.append((inv.id, "{} {}".format(inv.name, inv.ref)))
            elif inv.ref and inv.name == "/":
                res.append((inv.id, "{}".format(inv.ref)))
            else:
                return super(AccountMove, self).name_get()
        return res
