# Copyright 2023 Pol Reig (pol.reig@qubiq.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    extracting_ocr = fields.Boolean(default=False)

    def _save_form(self, ocr_results, no_ref=False):
        """
        Boolean to make the `invoice_date_due` field not readonly
        while executing the OCR function `_save_form`.
        """
        self.extracting_ocr = True
        res = super()._save_form(ocr_results, no_ref)
        self.extracting_ocr = False
        return res
