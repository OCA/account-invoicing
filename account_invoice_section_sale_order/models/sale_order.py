# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from collections import OrderedDict

from odoo import models
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import AccessError

from itertools import groupby

import time


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id.
        If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        # Incremental sequencing to keep the lines order on the invoice.
        invoice_item_sequence = 0
        for order in self:
            order = order.with_company(order.company_id)

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                continue

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                if not down_payment_section_added and line.is_downpayment:
                    # Create a dedicated section for the down payments
                    # (put at the end of the invoiceable_lines)
                    invoice_line_vals.append(
                        (0, 0, order._prepare_down_payment_section_line(
                            sequence=invoice_item_sequence,
                        )),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1
                invoice_line_vals.append(
                    (0, 0, line._prepare_invoice_line(
                        sequence=invoice_item_sequence,
                    )),
                )
                invoice_item_sequence += 1

            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(
                invoice_vals_list,
                key=lambda x: [x.get(
                    grouping_key
                ) for grouping_key in invoice_grouping_keys])
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):  # noqa
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']  # noqa
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,  # noqa
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence
        # of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence
        # only if there are less invoices than
        # orders, meaning a grouping might have been done.
        # This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing
        # in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])  # noqa
                    sequence += 1

        # Manage the creation of invoices in sudo because a salesperson
        # must be able to generate an invoice from a
        # sale order without "billing" access rights. However,
        # he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(
            default_move_type='out_invoice'
        ).create(invoice_vals_list)

        # 4) Some moves might actually be refunds: convert them
        # if the total amount is negative
        # We do this after the moves have been created since we
        # need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(
                lambda m: m.amount_total < 0
            ).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},  # noqa
                subtype_id=self.env.ref('mail.mt_note').id
            )
            if (
                len(move.line_ids.mapped(
                    move.line_ids._get_section_grouping()
                ))
                == 1
            ):
                continue
            sequence = 10
            move_lines = move._get_ordered_invoice_lines()
            # Group move lines according to their sale order
            section_grouping_matrix = OrderedDict()
            for move_line in move_lines:
                group = move_line._get_section_group()
                section_grouping_matrix.setdefault(
                    group, []
                ).append(move_line.id)
            # Prepare section lines for each group
            section_lines = []
            for group, move_line_ids in section_grouping_matrix.items():
                if group:
                    section_lines.append(
                        (
                            0,
                            0,
                            {
                                "name": group._get_invoice_section_name(),
                                "display_type": "line_section",
                                "sequence": sequence,
                                # see test:
                                # test_create_invoice_with_default_journal
                                # forcing the account_id is needed to avoid
                                # incorrect default value
                                "account_id": False,
                            },
                        )
                    )
                    sequence += 10
                for move_line in self.env["account.move.line"].browse(move_line_ids):  # noqa
                    move_line.sequence = sequence
                    sequence += 10
            move.line_ids = section_lines
        return moves

    def _get_invoice_section_name(self):
        """Returns the text for the section name."""
        self.ensure_one()
        naming_scheme = (
            self.partner_invoice_id.invoice_section_name_scheme
            or self.company_id.invoice_section_name_scheme
        )
        if naming_scheme:
            return safe_eval(naming_scheme, {"object": self, "time": time})
        elif self.client_order_ref:
            return "{} - {}".format(self.name, self.client_order_ref or "")
        else:
            return self.name
