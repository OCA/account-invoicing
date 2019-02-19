# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from logging import getLogger

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = getLogger(__name__)


class PurchaseBatchInvoicing(models.TransientModel):
    _name = "purchase.batch_invoicing"

    purchase_order_ids = fields.Many2many(
        comodel_name="purchase.order",
        string="Purchase orders",
        domain="[('invoice_status', '=', 'to invoice')]",
        required=True,
        readonly=True,
        default=lambda self: self._default_purchase_order_ids(),
    )
    grouping = fields.Selection(
        selection=[
            ("id", "Purchase Order"),
            ("partner_id", "Vendor"),
        ],
        required=True,
        default="id",
        help="Make one invoice for each...",
    )

    @api.model
    def _default_purchase_order_ids(self):
        """Get purchase orders from active ids."""
        try:
            return self.env["purchase.order"].search(
                self._purchase_order_domain(self.env.context["active_ids"])
            ).ids
        except KeyError:
            return False

    @api.model
    def _purchase_order_domain(self, ids=None):
        """Helper to filter current ids by those that are to invoice."""
        domain = [("invoice_status", "=", "to invoice")]
        if ids:
            domain += [("id", "in", ids)]
        pos = self.env["purchase.order"].search(domain)
        # Use only POs with less qty invoiced than the expected
        pos = pos.filtered(lambda order: (
            any(
                line.qty_invoiced < (
                    line.qty_received
                    if line.product_id.purchase_method == 'receive'
                    else line.product_qty
                )
            ) for line in order.order_line
        ))
        if len(domain) > 1:
            domain[1] = ("id", "in", pos.ids)
        return domain

    @api.multi
    def grouped_purchase_orders(self):
        """Purchase orders, applying current grouping.

        :return generator:
            Generator of grouped ``purchase.order`` recordsets.

            If :attr:`grouping` is ``id``, the generator will yield recordsets
            with 1 order each; if it is ``partner_id``, the yielded recordsets
            will contain all purchase orders from each vendor.
        """
        PurchaseOrder = self.env["purchase.order"]
        domain = self._purchase_order_domain(self.purchase_order_ids.ids)
        for group in self.mapped("purchase_order_ids.%s" % self.grouping):
            pos = PurchaseOrder.search(
                domain + [(self.grouping, "=", int(group))])
            if pos:
                yield pos

    @api.multi
    def action_batch_invoice(self):
        """Generate invoices for all selected purchase orders.

        :return dict:
            Window action to see the generated invoices.
        """
        invoices = self.env["account.invoice"]
        for pogroup in self.grouped_purchase_orders():
            invoice = invoices.create({
                "partner_id": pogroup.mapped("partner_id").id,
                "type": "in_invoice",
            })
            invoice._onchange_partner_id()
            for po in pogroup:
                invoice.currency_id = po.currency_id
                invoice.purchase_id = po
                invoice.purchase_order_change()
            invoices |= invoice
        if not invoices:
            raise UserError(_("No ready-to-invoice purchase orders selected."))
        invoices.compute_taxes()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "name": _("Generated Invoices"),
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", invoices.ids]],
        }

    @api.model
    def cron_invoice_all_pending(self, grouping="partner_id"):
        """Invoice all pending purchase orders."""
        _logger.info("Starting to invoice all pending purchase orders.")
        wizard = self.create({
            "purchase_order_ids": [
                (6, False, self.env["purchase.order"].search(
                    self._purchase_order_domain()).ids)],
            "grouping": grouping,
        })
        try:
            result = wizard.action_batch_invoice()
            _logger.info("Finished invoicing all pending purchase orders.")
            _logger.debug("Result: %r", result)
        except UserError as error:
            _logger.info(error.name)
            _logger.debug("Traceback:", exc_info=True)
