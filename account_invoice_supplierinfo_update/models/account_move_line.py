# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_supplierinfo(self):
        """Given an invoice line, return the supplierinfo that matches
        with product and supplier, if exist"""
        self.ensure_one()
        supplierinfos = self.product_id.seller_ids.filtered(
            lambda seller: seller.name == self.move_id.supplier_partner_id
        )
        return supplierinfos and supplierinfos[0] or False

    def _get_unit_price_in_purchase_uom(self):
        self.ensure_one()
        if not self.product_id:
            return self.price_unit
        uom = self.product_uom_id or self.product_id.uom_id
        return uom._compute_price(self.price_unit, self.product_id.uom_po_id)

    def _is_correct_price(self, supplierinfo):
        """Return True if the partner information matche with line info
        Overload this function in custom module if extra fields
        are added in supplierinfo. (discount for exemple)
        """
        self.ensure_one()
        return self._get_unit_price_in_purchase_uom() == supplierinfo.price

    def _prepare_supplier_wizard_line(self, supplierinfo):
        """Prepare the value that will proposed to user in the wizard
        to update supplierinfo"""
        self.ensure_one()
        price_unit = self._get_unit_price_in_purchase_uom()
        price_variation = False

        if supplierinfo:
            # Compute price variation
            if supplierinfo.price:
                price_variation = (
                    100 * (price_unit - supplierinfo.price) / supplierinfo.price
                )
            else:
                price_variation = False
        return {
            "product_id": self.product_id.id,
            "supplierinfo_id": supplierinfo and supplierinfo.id or False,
            "current_price": supplierinfo and supplierinfo.price or False,
            "new_price": price_unit,
            "current_min_quantity": supplierinfo and supplierinfo.min_qty or False,
            "new_min_quantity": supplierinfo and supplierinfo.min_qty or False,
            "price_variation": price_variation,
        }
