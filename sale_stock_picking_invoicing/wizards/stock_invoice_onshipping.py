# Copyright (C) 2020-TODAY KMEE
# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInvoiceOnshipping(models.TransientModel):

    _inherit = "stock.invoice.onshipping"

    def _build_invoice_values_from_pickings(self, pickings):
        invoice, values = super()._build_invoice_values_from_pickings(pickings)
        pick = fields.first(pickings)
        if pick.sale_id:
            # Refund case don't get values from Sale Dict
            # TODO: Should get any value?
            if self._get_invoice_type() != "out_refund":
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
                # Original dict from sale module, fields uncomment will be remove
                vals_to_remove = {
                    # "ref": self.client_order_ref or '',
                    "move_type",
                    # "narration": self.note,
                    "currency_id",
                    # "campaign_id": self.campaign_id.id,
                    # "medium_id": self.medium_id.id,
                    # "source_id": self.source_id.id,
                    "user_id",
                    "invoice_user_id",
                    # "team_id": self.team_id.id,
                    "partner_id",
                    # "partner_shipping_id": self.partner_shipping_id.id,
                    "fiscal_position_id",
                    # "partner_bank_id": self.company_id.partner_id.bank_ids.
                    # filtered(lambda bank: bank.company_id.id in
                    # (self.company_id.id, False))[:1].id,
                    "journal_id",  # company comes from the journal
                    "invoice_origin",
                    # "invoice_payment_term_id": self.payment_term_id.id,
                    # "payment_reference": self.reference,
                    # "transaction_ids": [(6, 0, self.transaction_ids.ids)],
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
                vals_to_remove = {
                    "display_type",
                    # "sequence": self.sequence,
                    "name",
                    "product_id",
                    "product_uom_id",
                    "quantity",
                    # "discount": self.discount,
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

    def _create_invoice(self, invoice_values):
        """Override this method if you need to change any values of the
        invoice and the lines before the invoice creation
        :param invoice_values: dict with the invoice and its lines
        :return: invoice
        """
        pickings = self._load_pickings()
        pick = fields.first(pickings)
        if pick.sale_id:
            invoice_item_sequence = (
                0  # Incremental sequencing to keep the lines order on the invoice.
            )

            order = pick.sale_id.with_company(pick.sale_id.company_id)

            invoiceable_lines = order._get_invoiceable_lines(final=True)

            # Get Sale Sequence
            sale_sequence_list = []
            for line in invoice_values.get("invoice_line_ids"):
                if line[2].get("sequence"):
                    sale_sequence_list.append(line[2].get("sequence"))

            invoice_item_sequence = max(sale_sequence_list) + 1

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                if not down_payment_section_added and line.is_downpayment:
                    # Create a dedicated section for the down payments
                    # (put at the end of the invoiceable_lines)
                    invoice_line_vals.append(
                        (
                            0,
                            0,
                            order._prepare_down_payment_section_line(
                                sequence=invoice_item_sequence,
                            ),
                        ),
                    )
                    down_payment_section_added = True

                if line.is_downpayment and line.price_unit:
                    value_down_payment = line._prepare_invoice_line()
                    invoice_line_vals.append(
                        (0, 0, value_down_payment),
                    )

                invoice_item_sequence += 1

            invoice_values["invoice_line_ids"] += invoice_line_vals

        moves = (
            self.env["account.move"]
            .sudo()
            .with_context(default_move_type="out_invoice")
            .create(invoice_values)
        )

        # TODO: Should Final field always True?
        final = True
        if final:
            moves.sudo().filtered(
                lambda m: m.amount_total < 0
            ).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view(
                "mail.message_origin_link",
                values={
                    "self": move,
                    "origin": move.line_ids.mapped("sale_line_ids.order_id"),
                },
                subtype_id=self.env.ref("mail.mt_note").id,
            )

        return moves
