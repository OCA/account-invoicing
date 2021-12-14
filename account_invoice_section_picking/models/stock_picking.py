# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models
from odoo.tools.safe_eval import safe_eval, time


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _get_invoice_section_name(self):
        """Returns the text for the section name."""
        section_names = []
        for pick in self:
            naming_scheme = (
                pick.partner_id.invoice_section_name_scheme
                or pick.company_id.invoice_section_name_scheme
            )
            if naming_scheme:
                section_names.append(
                    safe_eval(naming_scheme, {"object": pick, "time": time})
                )
            else:
                section_names.append(pick.name)
        return ", ".join(section_names)
