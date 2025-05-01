# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = [
        _name,
        "stock.invoice.state.mixin",
    ]

    def _get_taxes(self, fiscal_position, inv_type):
        """
        Map product taxes based on given fiscal position
        :param fiscal_position: account.fiscal.position recordset
        :param inv_type: string
        :return: account.tax recordset
        """
        product = self.mapped("product_id")
        product.ensure_one()
        if inv_type in ("out_invoice", "out_refund"):
            taxes = product.taxes_id
        else:
            taxes = product.supplier_taxes_id
        company_id = self.env.context.get("force_company", self.env.company.id)
        my_taxes = taxes.filtered(lambda r: r.company_id.id == company_id)
        return fiscal_position.map_tax(my_taxes)

    @api.model
    def _get_account(self, fiscal_position, account):
        """
        Map the given account with given fiscal position
        :param fiscal_position: account.fiscal.position recordset
        :param account: account.account recordset
        :return: account.account recordset
        """
        return fiscal_position.map_account(account)

    def _get_price_unit_invoice(self, inv_type, partner, qty=1):
        """
        Gets price unit for invoice
        :param inv_type: str
        :param partner: res.partner
        :param qty: float
        :return: float
        """
        product = self.mapped("product_id")
        product.ensure_one()
        if inv_type in ("in_invoice", "in_refund"):
            result = product.price
        else:
            # If partner given, search price in its sale pricelist
            if partner and partner.property_product_pricelist:
                product = product.with_context(
                    partner=partner.id,
                    quantity=qty,
                    pricelist=partner.property_product_pricelist.id,
                    uom=fields.first(self).product_uom.id,
                )
                result = product.price
            else:
                result = product.lst_price
        return result

    def _prepare_extra_move_vals(self, qty):
        """Copy invoice state for a new extra stock move"""
        values = super()._prepare_extra_move_vals(qty)
        values["invoice_state"] = self.invoice_state
        return values

    def _prepare_move_split_vals(self, uom_qty):
        """Copy invoice state for a new splitted stock move"""
        values = super()._prepare_move_split_vals(uom_qty)
        values["invoice_state"] = self.invoice_state
        return values

    def _action_cancel(self):
        res = super()._action_cancel()
        # The allowed group is defined in a noupdate xml data section.
        # This means that if someone updates the module to get this feature,
        # the group won't be created.
        allowed_group = self.env.ref(
            "stock_picking_invoicing.group_allow_to_cancel_stock_move_linked_to_invoice_bill",
            raise_if_not_found=False,
        )
        if allowed_group:
            # done moves out, built-in workflow deals with them,
            # also out moves linked to cancelled journal items
            moves = self.filtered(
                lambda it: it.state != "done"
                and it.invoice_line_ids.filtered(
                    lambda inv_line: inv_line.move_id.state != "cancel"
                )
            )
            if moves:
                if allowed_group not in self.env.user.groups_id:
                    move_references = ",".join(
                        moves.mapped(
                            lambda it: f"{it.reference}({it.product_id.default_code})"
                        )
                    )
                    raise UserError(
                        _(
                            "You cannot cancel a stock move linked to invoices/bills. "
                            'Only members of the "%(group_name)s" group can perform '
                            "this action. References: %(references)s",
                            group_name=allowed_group.name,
                            references=move_references,
                        )
                    )
        return res
