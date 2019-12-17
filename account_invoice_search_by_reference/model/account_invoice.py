# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("reference", operator, name), ("number", operator, name)]
        invoices = self.search(domain + args, limit=limit)
        return invoices.name_get()

    @api.multi
    @api.depends("reference", "number")
    def name_get(self):
        res = []
        for inv in self:
            if inv.reference and inv.number:
                res.append(
                    (inv.id, "{} {} {}".format(inv.number, inv.reference, inv.name or ""))
                )
            elif inv.reference and not inv.number:
                res.append((inv.id, "{} {}".format(inv.reference, inv.name or "")))
            else:
                return super(AccountInvoice, self).name_get()
        return res
