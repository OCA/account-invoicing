# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountEdiXmlUBL20(models.AbstractModel):
    _inherit = "account.edi.xml.ubl_20"

    def _import_fill_invoice_form(self, journal, tree, invoice, qty_factor):
        res = super()._import_fill_invoice_form(journal, tree, invoice, qty_factor)
        ref_node = tree.find("./{*}ID")
        if ref_node is not None:
            if invoice.is_purchase_document():
                invoice.supplier_invoice_number = ref_node.text
        return res
