# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class OneVatMixin(models.AbstractModel):
    _name = "one.vat.mixin"
    _description = "Abstract the methods needed to ensure only one VAT tax is selected."

    def _get_vat_taxes(self, field_name, company):
        vat_taxes = self[field_name].filtered(
            lambda r: r.is_vat and r.company_id == company
        )
        return vat_taxes

    def _check_only_one_vat_tax_field(self, field_name):
        loggedin_company = self.env.company
        for rec in self:
            company = rec.company_id or loggedin_company
            if company.account_tax_one_vat:
                vat_taxes = rec._get_vat_taxes(field_name, company)
                if len(vat_taxes) > 1:
                    msg = _(
                        "Multiple taxes of type VAT are selected. Only one is allowed."
                    )
                    raise ValidationError(msg)

    def _onchange_one_vat_tax_field(self, field_name):
        """Warning if multiple VAT taxes are selected."""
        company = self.company_id or self.env.company
        if company.account_tax_one_vat:
            try:
                self._check_only_one_vat_tax_field(field_name)
            except ValidationError:
                warning_mess = {
                    "title": _("More than one VAT tax selected!"),
                    "message": _("You selected more than one tax of type VAT."),
                }
                return {"warning": warning_mess}
        return {}
