# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockInvoiceStateMixin(models.AbstractModel):
    """
    Abstract model used to define invoice state with selection choices
    """
    _name = "stock.invoice.state.mixin"

    invoice_state = fields.Selection(
        selection=[
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable"),
        ],
        string="Invoice Status",
        default="none",
        help="Invoiced: an invoice already exists\n"
             "To Be Invoiced: need to be invoiced\n"
             "Not Applicable: no invoice to create",
        copy=False,
    )

    @api.multi
    def _set_as_invoiced(self):
        """
        Update invoice_state on current recordset to 'invoiced'
        :return: self recordset (where the updated has been executed)
        """
        return self._update_invoice_state('invoiced')

    @api.multi
    def _set_as_2binvoiced(self):
        """
        Update invoice_state on current recordset to '2binvoiced'
        :return: self recordset (where the updated has been executed)
        """
        return self._update_invoice_state('2binvoiced')

    @api.multi
    def _set_as_not_billable(self):
        """
        Update invoice_state on current recordset to 'invoiced'
        :return: self recordset (where the updated has been executed)
        """
        return self._update_invoice_state('none')

    @api.multi
    def _update_invoice_state(self, invoice_state):
        """
        Execute the write
        :param invoice_state: str
        :return: self recordset (where the updated has been executed)
        """
        records = self.filtered(lambda r: r.invoice_state != invoice_state)
        if records:
            records.write({
                'invoice_state': invoice_state,
            })
        return records
