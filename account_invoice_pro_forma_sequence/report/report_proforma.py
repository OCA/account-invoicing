# Copyright 2021 Lorenzo Battistini @ TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class ReportInvoiceProforma(models.AbstractModel):
    _name = "report.account_invoice_pro_forma_sequence.report_proforma"
    _description = "Pro-forma Invoice Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["account.move"].browse(docids)

        # Check if all documents have proforma numbers
        for doc in docs:
            if not doc.proforma_number:
                raise UserError(
                    _(
                        "Cannot print pro-forma invoice without a pro-forma number. "
                        "Please assign a pro-forma number first using the "
                        "'Assign Pro-forma Number' button."
                    )
                )

        return {
            "doc_ids": docids,
            "doc_model": "account.move",
            "docs": docs,
            "data": data,
        }
