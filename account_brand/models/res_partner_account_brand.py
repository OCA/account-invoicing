# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ResPartnerAccountBrand(models.Model):
    """This model is meant to be used in case we need to define different
    receivable/payable accounts for partners"""

    _name = "res.partner.account.brand"
    _description = "Receivable/Payable Partner Account By Brand"

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=False
    )
    account_id = fields.Many2one(
        comodel_name="account.account", string="Account", required=True
    )
    brand_id = fields.Many2one(
        comodel_name='res.partner',
        string='Brand',
        domain="[('type', '=', 'brand')]",
        required=True,
    )
    account_type = fields.Selection(
        string="Type",
        selection=[("payable", "Payable"), ("receivable", "Receivable")],
        required=True,
    )

    _sql_constraints = [
        (
            "unique_account_by_partner",
            "unique(partner_id, account_id, brand_id, account_type)",
            _("Partner has already an account set for this brand!"),
        )
    ]

    @api.onchange("account_type")
    def _onchange_account_type(self):
        self.ensure_one()
        self.update({"account_id": False})
        domain = [("id", "=", False)]
        if self.account_type == "payable":
            domain = [
                ("internal_type", "=", "payable"),
                ("deprecated", "=", False),
            ]
        elif self.account_type == "receivable":
            domain = [
                ("internal_type", "=", "receivable"),
                ("deprecated", "=", False),
            ]
        return {"domain": {"account_id": domain}}

    @api.model
    def _get_partner_account_by_brand(self, account_type, brand, partner):
        domain = [
            ("brand_id", "=", brand.id),
            ("account_type", "=", account_type),
        ]
        default_account = self.search(
            domain + [("partner_id", "=", False)], limit=1
        )
        account = False
        if partner:
            account = self.search(domain + [("partner_id", "=", partner.id)])
        return account or default_account
