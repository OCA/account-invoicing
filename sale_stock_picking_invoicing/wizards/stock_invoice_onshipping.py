# Copyright (C) 2020-TODAY KMEE
# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInvoiceOnshipping(models.TransientModel):

    _inherit = "stock.invoice.onshipping"

    def _build_invoice_values_from_pickings(self, pickings):
        invoice, values = super()._build_invoice_values_from_pickings(pickings)

        sale_pickings = pickings.filtered(lambda pk: pk.sale_id)
        # Refund case don't get values from Sale Dict
        # TODO: Should get any value?
        if sale_pickings and self._get_invoice_type() != "out_refund":
            # Case more than one Sale Order the fields below will be join
            # the others will be overwritting, as done in sale module,
            # one more field include here Note
            payment_refs = set()
            refs = set()
            # Include Narration
            narration = set()
            for pick in sale_pickings.sorted(key=lambda p: p.name):
                # Other modules can included new fields in Sale Order and include
                # this fields in the dict of creation Invoice from sale, for
                # example:
                # - account_payment_sale
                #  https://github.com/OCA/bank-payment/blob/14.0/
                #  account_payment_sale/models/sale_order.py#L41
                # - sale_commssion
                #  https://github.com/OCA/commission/blob/14.0/
                #  sale_commission/models/sale_order.py#L64
                # To avoid the necessity of a 'glue' module the method get the
                # values from _prepare_invoice but removed some fields of the
                # original method, given priority for values from
                # stock_picking_invoicing dict, for now it's seems the best to
                # way to avoid the 'glue' modules problem.
                sale_values = pick.sale_id._prepare_invoice()
                # Fields to Join
                # origins.add(sale_values["invoice_origin"])
                payment_refs.add(sale_values["payment_reference"])
                refs.add(sale_values["ref"])
                narration.add(sale_values["narration"])

                # Original dict from sale module, for reference:
                # Fields to get:
                #  "ref": self.client_order_ref or ''
                #  "narration": self.note,
                #  "campaign_id": self.campaign_id.id,
                #  "medium_id": self.medium_id.id,
                #  "source_id": self.source_id.id,
                #  "team_id": self.team_id.id,
                #  "partner_shipping_id": self.partner_shipping_id.id,
                #  "partner_bank_id": self.company_id.partner_id.bank_ids.
                #      filtered(lambda bank: bank.company_id.id in
                #      (self.company_id.id, False))[:1].id,
                #  "invoice_payment_term_id": self.payment_term_id.id,
                #  "payment_reference": self.reference,
                #  "transaction_ids": [(6, 0, self.transaction_ids.ids)],

                # Fields to remove
                vals_to_remove = {
                    "move_type",
                    "currency_id",
                    "user_id",
                    "invoice_user_id",
                    "partner_id",
                    "fiscal_position_id",
                    "journal_id",  # company comes from the journal
                    "invoice_origin",
                    "invoice_line_ids",
                    "company_id",
                    # Another fields
                    "__last_update",
                    "display_name",
                }
                sale_values_rm = {
                    k: sale_values[k] for k in set(sale_values) - vals_to_remove
                }

                values.update(sale_values_rm)

            # Fields to join
            if len(sale_pickings) > 1:
                values.update(
                    {
                        "ref": ", ".join(refs)[:2000],
                        # In this case Origin get Pickings Names
                        # "invoice_origin": ", ".join(origins),
                        "payment_reference": len(payment_refs) == 1
                        and payment_refs.pop()
                        or False,
                        "narration": ", ".join(narration),
                    }
                )

        return invoice, values

    # Check the comment below
    # def _get_picking_key(self, picking):
    #    key = super()._get_picking_key(picking)
    #    if picking.sale_id:
    #        key = key + (
    #            picking.sale_id.payment_term_id,
    #            picking.sale_id.fiscal_position_id,
    #            picking.sale_id.commitment_date,
    #            picking.sale_id.analytic_account_id,
    #            picking.sale_id.pricelist_id,
    #            picking.sale_id.company_id,
    #        )
    #    return key

    def _get_move_key(self, move):
        key = super()._get_move_key(move)
        if move.sale_line_id:
            # TODO: Analise if Sale Lines should be grouped.
            #  For now remains a problem https://github.com/odoo/odoo/pull/77195
            #  with field qty_invoiced at sale.order.line, when a invoice line
            #  has more than one sale line related the field show the total QTY
            #  of those lines, e.g:
            #  product_uom_qty | qty_invoiced
            #       2.0        |  4.0
            # key = key + (
            #    move.sale_line_id.price_unit,
            #    move.sale_line_id.customer_lead,
            #    move.sale_line_id.currency_id,
            #    move.sale_line_id.tax_id,
            #    move.sale_line_id.analytic_tag_ids,
            # )
            key = key + (move.sale_line_id,)

        return key

    def _get_invoice_line_values(self, moves, invoice_values, invoice):
        values = super()._get_invoice_line_values(moves, invoice_values, invoice)
        move = fields.first(moves)
        if move.sale_line_id:
            # Vals informed in any case
            values["sale_line_ids"] = [(6, 0, moves.sale_line_id.ids)]
            values[
                "analytic_account_id"
            ] = moves.sale_line_id.order_id.analytic_account_id.id
            values["analytic_tag_ids"] = [
                (6, 0, moves.sale_line_id.analytic_tag_ids.ids)
            ]
            # Refund case don't get values from Sale Line Dict
            # TODO: Should get any value?
            if self._get_invoice_type() != "out_refund":
                # Same make above, get fields informed in Sale Line dict
                sale_line_values = move.sale_line_id._prepare_invoice_line()
                # Original fields from sale module
                # Fields do get
                #     "sequence": self.sequence,
                #     "discount": self.discount,

                # Fields to remove
                vals_to_remove = {
                    "display_type",
                    "name",
                    "product_id",
                    "product_uom_id",
                    "quantity",
                    "price_unit",
                    "tax_ids",
                    "analytic_account_id",
                    "analytic_tag_ids",
                    "sale_line_ids",
                    # another fields
                    "__last_update",
                    "display_name",
                }
                sale_line_values_rm = {
                    k: sale_line_values[k]
                    for k in set(sale_line_values) - vals_to_remove
                }
                values.update(sale_line_values_rm)

        return values
