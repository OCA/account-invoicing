# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountEdiXmlUBL20(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_20"

    def _import_fill_invoice_form(self, journal, tree, invoice, qty_factor):
        res = super()._import_fill_invoice_form(journal, tree, invoice, qty_factor)
        if not invoice.is_purchase_document():
            return res
        invoice_total_node = tree.find("./{*}LegalMonetaryTotal/{*}TaxInclusiveAmount")
        if invoice_total_node is not None:
            invoice.check_total = float(invoice_total_node.text)
        return res
