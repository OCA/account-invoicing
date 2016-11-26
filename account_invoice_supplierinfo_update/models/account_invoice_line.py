# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _get_supplierinfo(self):
        """Given an invoice line, return the supplierinfo that matches
        with product and supplier, if exist"""
        self.ensure_one()
        supplierinfos = (self.product_id.seller_ids.filtered(
            lambda seller: seller.name == self.invoice_id.supplier_partner_id))
        return supplierinfos and supplierinfos[0] or False

    @api.multi
    def _get_partnerinfo(self, supplierinfo):
        """Given an invoice line and a supplierinfo, return the partnerinfo
        that matches with line info, if exist"""
        self.ensure_one()
        if not len(supplierinfo.pricelist_ids):
            return False
        else:
            # Select partnerinfo, depending of the quantity
            for partnerinfo in supplierinfo.pricelist_ids.sorted(
                    key=lambda r: r.min_quantity):
                if partnerinfo.min_quantity <= self.quantity:
                    return partnerinfo
            return False

    @api.multi
    def _is_correct_partner_info(self, partnerinfo):
        """Return True if the partner information matche with line info
            Overload this function in custom module if extra fields
            are added in partnerinfo. (discount for exemple)
        """
        self.ensure_one()
        return self.price_unit == partnerinfo.price

    @api.multi
    def _prepare_supplier_wizard_line(self, supplierinfo, partnerinfo):
        """Prepare the value that will proposed to user in the wizard
        to update supplierinfo"""
        self.ensure_one()
        price_variation = False
        if not supplierinfo:
            state = 'new_supplierinfo'
        elif not partnerinfo:
            state = 'new_partnerinfo'
        else:
            state = 'update_partnerinfo'
            # Compute price variation
            if partnerinfo.price:
                price_variation = 100 *\
                    (self.price_unit - partnerinfo.price) / partnerinfo.price
            else:
                price_variation = False
        return {
            'product_id': self.product_id.id,
            'supplierinfo_id': supplierinfo and supplierinfo.id or False,
            'partnerinfo_id': partnerinfo and partnerinfo.id or False,
            'current_price': partnerinfo and partnerinfo.price or False,
            'new_price': self.price_unit,
            'current_min_quantity':
                partnerinfo and partnerinfo.min_quantity or False,
            'new_min_quantity':
                partnerinfo and partnerinfo.min_quantity or False,
            'state': state,
            'price_variation': price_variation,
        }
