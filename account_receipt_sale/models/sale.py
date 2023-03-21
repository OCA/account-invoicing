from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    receipts = fields.Boolean()
    receipt_ids = fields.Many2many(
        comodel_name="account.move",
        string="Receipts",
        compute="_compute_receipt_ids",
        readonly=True,
        copy=False,
        search="_search_receipt_ids",
    )
    receipt_count = fields.Integer(
        string="Receipt Count",
        compute="_compute_receipt_ids",
        readonly=True,
    )

    @api.depends(
        "order_line.invoice_lines",
    )
    def _compute_receipt_ids(self):
        for order in self:
            receipts = order.order_line.invoice_lines.move_id.filtered(
                lambda r: r.move_type == "out_receipt"
            )
            order.receipt_ids = receipts
            order.receipt_count = len(receipts)

    def _search_receipt_ids(self, operator, value):
        # Basically copied from _search_invoice_ids,
        # just using out_receipt instead of out_invoice and out_refund
        if operator == "in" and value:
            self.env.cr.execute(
                """
                SELECT array_agg(so.id)
                    FROM sale_order so
                    JOIN sale_order_line sol ON sol.order_id = so.id
                    JOIN sale_order_line_invoice_rel soli_rel ON soli_rel.order_line_id = sol.id
                    JOIN account_move_line aml ON aml.id = soli_rel.invoice_line_id
                    JOIN account_move am ON am.id = aml.move_id
                WHERE
                    am.move_type = 'out_receipt' AND
                    am.id = ANY(%s)
            """,
                (list(value),),
            )
            so_ids = self.env.cr.fetchone()[0] or []
            return [("id", "in", so_ids)]
        elif operator == "=" and not value:
            order_ids = self._search(
                [
                    ("order_line.invoice_lines.move_id.move_type", "=", "out_receipt"),
                ]
            )
            return [("id", "not in", order_ids)]
        return [
            "&",
            ("order_line.invoice_lines.move_id.move_type", "=", "out_receipt"),
            ("order_line.invoice_lines.move_id", operator, value),
        ]

    def action_view_receipt(self):
        # Basically the same as what happens in action_view_invoice
        receipts = self.mapped("receipt_ids")
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_receipt_type"
        )
        if len(receipts) > 1:
            action["domain"] = [("id", "in", receipts.ids)]
        elif len(receipts) == 1:
            form_view = [(self.env.ref("account.view_move_form").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = receipts.id
        else:
            action = {"type": "ir.actions.act_window_close"}

        context = {
            "default_move_type": "out_receipt",
        }
        if len(self) == 1:
            context.update(
                {
                    "default_partner_id": self.partner_id.id,
                    "default_partner_shipping_id": self.partner_shipping_id.id,
                    "default_invoice_payment_term_id": self.payment_term_id.id
                    or self.partner_id.property_payment_term_id.id
                    or self.env["account.move"]
                    .default_get(["invoice_payment_term_id"])
                    .get("invoice_payment_term_id"),
                    "default_invoice_origin": self.name,
                    "default_user_id": self.user_id.id,
                }
            )
        action["context"] = context
        return action

    @api.onchange("partner_id")
    def _onchange_partner_receipts_sale(self):
        self.receipts = self.partner_id.use_receipts

    @api.onchange("fiscal_position_id")
    def _onchange_fiscal_position_id_receipts(self):
        if self.fiscal_position_id:
            self.receipts = self.fiscal_position_id.receipts

    def _prepare_invoice(self):
        invoice_values = super()._prepare_invoice()
        if self.receipts:
            invoice_values["move_type"] = "out_receipt"
            self.env["account.move"]._update_receipts_journal([invoice_values])
        return invoice_values

    @api.model
    def create(self, values):
        order = super().create(values)
        if "partner_id" in values and "receipts" not in values:
            order._onchange_partner_receipts_sale()
        if "fiscal_position_id" in values and "receipts" not in values:
            order._onchange_fiscal_position_id_receipts()
        return order

    def write(self, values):
        res = super().write(values)
        if "partner_id" in values and "receipts" not in values:
            for order in self:
                order._onchange_partner_receipts_sale()
        if "fiscal_position_id" in values and "receipts" not in values:
            for order in self:
                order._onchange_fiscal_position_id_receipts()
        return res


class OrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_untaxed_amount_invoiced(self):
        super()._compute_untaxed_amount_invoiced()
        for line in self:
            amount_receipt = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.move_id.state == "posted":
                    invoice_date = (
                        invoice_line.move_id.invoice_date or fields.Date.today()
                    )
                    if invoice_line.move_id.move_type == "out_receipt":
                        amount_receipt += invoice_line.currency_id._convert(
                            invoice_line.price_subtotal,
                            line.currency_id,
                            line.company_id,
                            invoice_date,
                        )
            line.untaxed_amount_invoiced += amount_receipt

    def _get_invoice_qty(self):
        super()._get_invoice_qty()
        for line in self:
            qty_receipt = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.move_id.state != "cancel":
                    if invoice_line.move_id.move_type == "out_receipt":
                        qty_receipt += invoice_line.product_uom_id._compute_quantity(
                            invoice_line.quantity, line.product_uom
                        )
            line.qty_invoiced += qty_receipt
