# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    def _get_to_validate_message_name(self):
        name = super(TierValidation, self)._get_to_validate_message_name()
        if self.type == "in_invoice":
            name = _("Bill")
        elif self.type == "in_refund":
            name = _("Refund")
        elif self.type == "out_invoice":
            name = _("Invoice")
        elif self.type == "out_refund":
            name = _("Credit Note")
        return name
