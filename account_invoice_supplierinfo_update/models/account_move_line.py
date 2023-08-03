# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.tools import float_compare


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_supplierinfo(self):
        """Given an invoice line, return the supplierinfo that matches
        with product and supplier, if exist"""
        self.ensure_one()
        supplierinfos = self.product_id.seller_ids.filtered(
            lambda seller: seller.partner_id == self.move_id.supplier_partner_id
        )
        return supplierinfos and supplierinfos[0] or False

    def _is_matching_supplierinfo(self, supplierinfo):
        """Return True if the partner information matches with line information
        Overload this function in custom module if extra fields
        are added in supplierinfo. (discount for exemple)
        """
        self.ensure_one()
        return (
            not self.product_uom_id or self.product_uom_id == supplierinfo.product_uom
        ) and not float_compare(
            self.price_unit,
            supplierinfo.price,
            precision_rounding=self.move_id.currency_id.rounding,
        )

    def _prepare_supplier_wizard_line(self, supplierinfo):
        """Prepare the value that will proposed to user in the wizard
        to update supplierinfo"""
        self.ensure_one()
        return {
            "product_id": self.product_id.id,
            "supplierinfo_id": supplierinfo and supplierinfo.id or False,
            "current_price": supplierinfo and supplierinfo.price or False,
            "new_price": self.price_unit,
            "current_uom_id": supplierinfo and supplierinfo.product_uom.id or False,
            "new_uom_id": self.product_uom_id.id or self.product_id.uom_po_id.id,
            "current_min_quantity": supplierinfo and supplierinfo.min_qty or False,
            "new_min_quantity": supplierinfo and supplierinfo.min_qty or False,
        }
