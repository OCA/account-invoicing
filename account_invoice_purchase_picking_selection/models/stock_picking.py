from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools.float_utils import float_is_zero


class StockPicking(models.Model):
    _inherit = "stock.picking"

    received_invoiced_line_ids = fields.One2many(
        "account.move.line",
        "picking_invoiced_id",
        string="Invoiced Lines",
        copy=False,
    )
    received_invoiced_status = fields.Selection(
        [
            ("no", "Nothing to Bill"),
            ("to invoice", "Waiting Bills"),
            ("invoiced", "Fully Billed"),
        ],
        string="Billing Status",
        compute="_compute_received_invoiced_status",
        store=True,
        readonly=True,
        copy=False,
        default="no",
    )

    @api.depends(
        "state", "move_ids.qty_received_to_invoice", "purchase_id.invoice_status"
    )
    def _compute_received_invoiced_status(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for picking in self:
            if picking.state != "done" or not picking.purchase_id:
                picking.received_invoiced_status = "no"
                continue
            if picking.purchase_id.invoice_status == "invoiced":
                picking.received_invoiced_status = "invoiced"
                continue
            if any(
                not float_is_zero(
                    move.qty_received_to_invoice, precision_digits=precision
                )
                for move in picking.move_ids
            ):
                picking.received_invoiced_status = "to invoice"
            elif (
                all(
                    float_is_zero(
                        move.qty_received_to_invoice, precision_digits=precision
                    )
                    for move in picking.move_ids
                )
                and picking.received_invoiced_line_ids
            ):
                picking.received_invoiced_status = "invoiced"
            else:
                picking.received_invoiced_status = "no"

    @api.depends_context("filter_picking_autocomplete")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        if self.env.context.get("filter_picking_autocomplete"):
            for picking in self:
                display_name = picking.display_name
                if picking.purchase_id:
                    display_name += f" - {picking.purchase_id.name}"
                if picking.purchase_id.partner_ref:
                    display_name += f" - {picking.purchase_id.partner_ref}"
                picking.display_name = display_name
        return res

    def search(self, domain, offset=0, limit=None, order=None):
        if self.env.context.get("filter_picking_autocomplete"):
            # inject the domain to filter only the pickings pending to be invoiced
            domain.extend(self._get_picking_extra_domain())
        return super().search(domain, offset=offset, limit=limit, order=order)

    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        domain = domain or []
        if self.env.context.get("filter_picking_autocomplete"):
            # inject the domain to filter only the pickings pending to be invoiced
            domain.extend(self._get_picking_extra_domain())
        return super().read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )

    @api.model
    def _search_display_name(self, operator, value):
        if self.env.context.get("filter_picking_autocomplete"):
            base_domain = self._get_picking_extra_domain()
            picking_domain = base_domain
            if value:
                picking_domain = expression.AND(
                    [base_domain, self._get_name_search_domain(operator, value)]
                )
            return picking_domain
        return super()._search_display_name(operator, value)

    @api.model
    def _get_picking_extra_domain(self):
        # This method is used to filter the pickings that are pending to be invoiced
        company_id = self.env.context.get("invoice_company_id") or self.env.company.id
        partner_id = self.env.context.get("invoice_partner_id")
        domain = [
            ("state", "=", "done"),
            ("picking_type_id.code", "=", "incoming"),
            ("company_id", "=", company_id),
            ("received_invoiced_status", "=", "to invoice"),
        ]
        if partner_id:
            domain.append(("partner_id.commercial_partner_id", "=", partner_id))
        return domain

    @api.model
    def _get_name_search_domain(self, operator, name):
        # This method is used to filter the pickings
        # based on the name written by the user in the many2one field
        return expression.OR(
            [
                [("name", operator, name)],
                [
                    "|",
                    ("purchase_id.name", operator, name),
                    ("purchase_id.partner_ref", operator, name),
                ],
            ]
        )
