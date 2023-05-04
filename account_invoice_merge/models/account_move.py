# Copyright 2004-2010 Tiny SPRL (http://tiny.be).
# Copyright 2010-2011 Elico Corp.
# Copyright 2016 Acsone (https://www.acsone.eu/)
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2019 Okia SPRL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import numbers

from odoo import api, models
from odoo.tools import float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_invoice_key_cols(self):
        return [
            "partner_id",
            "user_id",
            "move_type",
            "currency_id",
            "journal_id",
            "company_id",
            "partner_bank_id",
        ]

    @api.model
    def _get_invoice_line_key_cols(self):
        fields = [
            "name",
            "discount",
            "tax_ids",
            "price_unit",
            "product_id",
            "account_id",
            "analytic_distribution",
            "product_uom_id",
        ]
        for field in [
            "sale_line_ids",  # odoo/sale
            "purchase_line_id",  # odoo/purchase
            "purchase_price",  # OCA/account_invoice_margin
        ]:
            if field in self.env["account.move.line"]._fields:
                fields.append(field)
        return fields

    @api.model
    def _get_first_invoice_fields(self, invoice):
        return {
            "invoice_origin": "%s" % (invoice.invoice_origin or "",),
            "partner_id": invoice.partner_id.id,
            "journal_id": invoice.journal_id.id,
            "user_id": invoice.user_id.id,
            "currency_id": invoice.currency_id.id,
            "company_id": invoice.company_id.id,
            "move_type": invoice.move_type,
            "state": "draft",
            "payment_reference": "%s" % (invoice.payment_reference or "",),
            "name": "%s" % (invoice.name or "",),
            "fiscal_position_id": invoice.fiscal_position_id.id,
            "invoice_payment_term_id": invoice.invoice_payment_term_id.id,
            "invoice_line_ids": {},
            "partner_bank_id": invoice.partner_bank_id.id,
        }

    @api.model
    def _get_sum_fields(self):
        return ["quantity"]

    @api.model
    def _get_invoice_line_vals(self, line):
        field_names = self._get_invoice_line_key_cols() + self._get_sum_fields()
        vals = {}
        origin_vals = line._convert_to_write(line._cache)
        for field_name, val in origin_vals.items():
            if field_name in field_names:
                vals[field_name] = val
        return vals

    def _get_draft_invoices(self):
        """Overridable function to return draft invoices to merge"""
        return self.filtered(lambda x: x.state == "draft")

    def make_key(self, br, fields):
        """
        Return a hashable key
        """
        list_key = []
        for field in fields:
            field_val = getattr(br, field)
            if isinstance(field_val, dict):
                field_val = str(field_val)
            elif isinstance(field_val, models.Model):
                field_val = tuple(sorted(field_val.ids))
            list_key.append((field, field_val))
        list_key.sort()
        return tuple(list_key)

    # flake8: noqa: C901
    def do_merge(
        self, keep_references=True, date_invoice=False, remove_empty_invoice_lines=True
    ):
        """
        To merge similar type of account invoices.
        Invoices will only be merged if:
        * Account invoices are in draft
        * Account invoices belong to the same partner
        * Account invoices are have same company, partner, address, currency,
          journal, currency, salesman, account, type
        Lines will only be merged if:
        * Invoice lines are exactly the same except for the quantity and unit

         @param self: The object pointer.
         @param keep_references: If True, keep reference of original invoices

         @return: new account invoice id

        """

        # compute what the new invoices should contain
        new_invoices = {}
        seen_origins = {}
        seen_client_refs = {}
        sum_fields = self._get_sum_fields()

        for account_invoice in self._get_draft_invoices():
            invoice_key = self.make_key(account_invoice, self._get_invoice_key_cols())
            new_invoice = new_invoices.setdefault(invoice_key, ({}, []))
            origins = seen_origins.setdefault(invoice_key, set())
            client_refs = seen_client_refs.setdefault(invoice_key, set())
            new_invoice[1].append(account_invoice.id)
            invoice_infos = new_invoice[0]
            if not invoice_infos:
                invoice_infos.update(self._get_first_invoice_fields(account_invoice))
                origins.add(account_invoice.invoice_origin)
                client_refs.add(account_invoice.payment_reference)
                if not keep_references:
                    invoice_infos.pop("name")
            else:
                if (
                    account_invoice.name
                    and keep_references
                    and invoice_infos.get("name") != account_invoice.name
                ):
                    invoice_infos["name"] = (
                        (invoice_infos["name"] or "") + " " + account_invoice.name
                    )
                if (
                    account_invoice.invoice_origin
                    and account_invoice.invoice_origin not in origins
                ):
                    invoice_infos["invoice_origin"] = (
                        (invoice_infos["invoice_origin"] or "")
                        + " "
                        + account_invoice.invoice_origin
                    )
                    origins.add(account_invoice.invoice_origin)
                if (
                    account_invoice.payment_reference
                    and account_invoice.payment_reference not in client_refs
                ):
                    invoice_infos["payment_reference"] = (
                        (invoice_infos["payment_reference"] or "")
                        + " "
                        + account_invoice.payment_reference
                    )
                    client_refs.add(account_invoice.payment_reference)

            for invoice_line in account_invoice.invoice_line_ids:
                line_key = self.make_key(
                    invoice_line, self._get_invoice_line_key_cols()
                )
                o_line = invoice_infos["invoice_line_ids"].setdefault(line_key, {})

                if o_line:
                    # merge the line with an existing line
                    for sum_field in sum_fields:
                        if sum_field in invoice_line._fields:
                            sum_val = invoice_line[sum_field]
                            if isinstance(sum_val, numbers.Number):
                                o_line[sum_field] += sum_val
                else:
                    # append a new "standalone" line
                    o_line.update(self._get_invoice_line_vals(invoice_line))

        allinvoices = []
        allnewinvoices = []
        invoices_info = {}
        old_invoices = self.env["account.move"]
        qty_prec = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for invoice_key, (invoice_data, old_ids) in new_invoices.items():
            # skip merges with only one invoice
            if len(old_ids) < 2:
                allinvoices += old_ids or []
                continue

            if remove_empty_invoice_lines:
                invoice_data["invoice_line_ids"] = [
                    (0, 0, value)
                    for value in invoice_data["invoice_line_ids"].values()
                    if not float_is_zero(value["quantity"], precision_digits=qty_prec)
                ]
            else:
                invoice_data["invoice_line_ids"] = [
                    (0, 0, value) for value in invoice_data["invoice_line_ids"].values()
                ]

            if date_invoice:
                invoice_data["invoice_date"] = date_invoice

            # create the new invoice
            newinvoice = self.with_context(is_merge=True).create(invoice_data)
            invoices_info.update({newinvoice.id: old_ids})
            allinvoices.append(newinvoice.id)
            allnewinvoices.append(newinvoice)
            # cancel old invoices
            old_invoices = self.env["account.move"].browse(old_ids)
            old_invoices.with_context(is_merge=True).button_cancel()
        self.merge_callback(invoices_info, old_invoices)
        return invoices_info

    @staticmethod
    def order_line_update_invoice_lines(todos, all_old_inv_line):
        for todo in todos:
            for line in todo.order_line:
                invoice_line = line.invoice_lines.filtered(
                    lambda x: x.parent_state != "cancel" or x.id not in all_old_inv_line
                )
                if invoice_line:
                    line.write({"invoice_lines": [(6, 0, invoice_line.ids)]})

    @api.model
    def merge_callback(self, invoices_info, old_invoices):
        # Make link between original sale order
        # None if sale is not installed
        # None if purchase is not installed
        if invoices_info:
            all_old_inv_line = old_invoices.mapped("invoice_line_ids").ids
            if "sale.order" in self.env.registry:
                sale_todos = old_invoices.mapped(
                    "invoice_line_ids.sale_line_ids.order_id"
                )
                self.order_line_update_invoice_lines(sale_todos, all_old_inv_line)

            if "purchase.order" in self.env.registry:
                purchase_todos = old_invoices.mapped(
                    "invoice_line_ids.purchase_line_id.order_id"
                )
                self.order_line_update_invoice_lines(purchase_todos, all_old_inv_line)
