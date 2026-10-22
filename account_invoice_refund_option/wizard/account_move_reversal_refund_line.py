from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveReversalRefundLine(models.TransientModel):
    _name = "account.move.reversal.refund.line"
    _description = "Account Move Reversal Refund Line"

    wizard_id = fields.Many2one("account.move.reversal", required=True)
    move_ids = fields.Many2many(
        related="wizard_id.move_ids",
    )
    available_product_ids = fields.Many2many(
        "product.product",
        compute="_compute_available_product_ids",
    )
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain="[('id', 'in', available_product_ids)]",
    )
    quantity = fields.Float(
        compute="_compute_quantity",
        precompute=True,
        digits="Product Unit of Measure",
        readonly=False,
        store=True,
    )

    @api.depends("move_ids")
    def _compute_available_product_ids(self):
        for record in self:
            record.available_product_ids = record.mapped("move_ids.line_ids.product_id")

    @api.depends("product_id", "move_ids")
    def _compute_quantity(self):
        for record in self:
            if not record.product_id:
                record.quantity = 0.0
                continue
            line = self.env["account.move.line"].search(
                [
                    ("move_id", "in", record.move_ids.ids),
                    ("product_id", "=", record.product_id.id),
                ],
                limit=1,
            )
            record.quantity = line.quantity

    @api.constrains("product_id", "quantity")
    def _check_quantity(self):
        for record in self:
            if not record.product_id:
                continue
            product_id = record.product_id.id
            max_qty_refund = max(
                record.move_ids.line_ids.filtered(
                    lambda line, pr=product_id: line.product_id.id == pr
                ).mapped("quantity"),
                default=0.0,
            )
            if record.quantity > max_qty_refund:
                raise ValidationError(
                    self.env._(
                        "The refund quantity for %s must be %s or less."
                        " Please reduce the quantity and try again.",
                        record.product_id.display_name,
                        max_qty_refund,
                    )
                )
