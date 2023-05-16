# Copyright 2023 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountTaxChange(models.Model):
    _name = "account.tax.change"
    _description = "Tax change mapping"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    date = fields.Date(required=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    change_line_ids = fields.One2many(
        comodel_name="account.tax.change.line",
        inverse_name="tax_change_id",
        string="Mapping",
    )

    _sql_constraints = [
        (
            "name_company_date_uniq",
            "unique(name, company_id, date)",
            "A tax change already exists for this company at this date.",
        ),
    ]


class AccountTaxChangeLine(models.Model):
    _name = "account.tax.change.line"
    _description = "Tax change mapping line"
    _check_company_auto = True

    tax_change_id = fields.Many2one(
        comodel_name="account.tax.change",
        ondelete="cascade",
        required=True,
        index=True,
    )
    company_id = fields.Many2one(related="tax_change_id.company_id")
    tax_src_id = fields.Many2one(
        comodel_name="account.tax",
        ondelete="cascade",
        string="From tax",
        required=True,
        check_company=True,
        index=True,
    )
    type_tax_use = fields.Selection(
        related="tax_src_id.type_tax_use",
    )
    tax_dest_id = fields.Many2one(
        comodel_name="account.tax",
        ondelete="cascade",
        string="To tax",
        required=True,
        check_company=True,
        domain="[('id', '!=', tax_src_id), ('type_tax_use', '=', type_tax_use)]",
    )

    @api.constrains("tax_src_id", "tax_dest_id")
    def _check_type_tax_use(self):
        for line in self:
            if not line.tax_src_id or not line.tax_dest_id:
                continue
            if line.tax_src_id.type_tax_use != line.tax_dest_id.type_tax_use:
                raise ValidationError(_("Taxes From/To have to share the same type."))
