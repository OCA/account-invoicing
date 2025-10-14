# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models

from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template(model="account.journal")
    def _get_account_receipt_journal(self, template_code):
        return {
            "sale_receipts": {
                "name": self.env._("Sale Receipts Journal"),
                "code": self.env._("S-REC"),
                "type": "sale",
                "sequence": 99,
                "receipts": True,
            },
            "purchase_receipts": {
                "name": self.env._("Purchase Receipts Journal"),
                "code": self.env._("P-REC"),
                "type": "purchase",
                "sequence": 99,
                "receipts": True,
            },
        }
