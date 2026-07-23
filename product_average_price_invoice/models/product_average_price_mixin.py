# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.tools import format_date

AVG_PRICE_FIELDS = {
    "in_invoice": "avg_purchase_price",
    "out_invoice": "avg_sale_price",
}


class ProductAveragePriceMixin(models.AbstractModel):
    _name = "product.average.price.mixin"
    _description = "Product Average Invoiced Price Mixin"

    avg_purchase_price = fields.Float(
        string="APP",
        digits="Product Price",
        copy=False,
        company_dependent=True,
        help="Average purchase unit price calculated from posted vendor bills, "
        "without taxes or added costs. A template averages all its variants.",
    )
    avg_purchase_price_date_from = fields.Date(company_dependent=True)
    avg_purchase_price_date_to = fields.Date(company_dependent=True)
    avg_purchase_price_period = fields.Char(
        compute="_compute_avg_price_periods",
        help="Date range the stored avg_purchase_price was computed for.",
    )
    avg_sale_price = fields.Float(
        string="ASP",
        digits="Product Price",
        copy=False,
        company_dependent=True,
        help="Average sale unit price calculated from posted customer invoices, "
        "without taxes or added costs. A template averages all its variants.",
    )
    avg_sale_price_date_from = fields.Date(company_dependent=True)
    avg_sale_price_date_to = fields.Date(company_dependent=True)
    avg_sale_price_period = fields.Char(
        compute="_compute_avg_price_periods",
        help="Date range the stored avg_sale_price was computed for.",
    )

    @api.depends_context("company")
    @api.depends(
        "avg_purchase_price_date_from",
        "avg_purchase_price_date_to",
        "avg_sale_price_date_from",
        "avg_sale_price_date_to",
    )
    def _compute_avg_price_periods(self):
        step_days, max_steps = self._get_avg_price_window()
        no_data = _("No data (last %(days)s days)") % {"days": step_days * max_steps}
        for record in self:
            for prefix in AVG_PRICE_FIELDS.values():
                date_from = record["%s_date_from" % prefix]
                date_to = record["%s_date_to" % prefix]
                record["%s_period" % prefix] = (
                    _("From %(start)s to %(end)s")
                    % {
                        "start": format_date(self.env, date_from),
                        "end": format_date(self.env, date_to),
                    }
                    if date_from and date_to
                    else no_data
                )

    @api.model
    def _get_avg_price_window(self):
        """Return the ``(step_days, max_steps)`` of the expanding window."""
        company = self.env.company
        return (
            max(company.avg_price_step_days, 1),
            max(company.avg_price_max_steps, 1),
        )

    def _avg_price_products(self):
        """Variants whose invoices feed this record's averages."""
        raise NotImplementedError

    def _avg_price_domain(self, products, move_type, date_from, date_to):
        """Invoice lines of ``products`` posted in the given period."""
        if not (products and date_from and date_to):
            return [("id", "=", False)]
        return [
            ("product_id", "in", products.ids),
            ("parent_state", "=", "posted"),
            ("display_type", "=", "product"),
            ("move_id.move_type", "=", move_type),
            ("move_id.invoice_date", ">=", date_from),
            ("move_id.invoice_date", "<=", date_to),
            ("company_id", "=", self.env.company.id),
        ]

    def _get_avg_price_values(self, move_type):
        """Return the values to store for the ``move_type`` average price.
        The window starts at ``step_days`` and is widened one step at a time,
        so the first one holding invoiced quantity wins. When the widest one
        has no data, a zero average without period is stored.
        """
        self.ensure_one()
        prefix = AVG_PRICE_FIELDS[move_type]
        products = self._avg_price_products()
        date_to = fields.Date.context_today(self)
        step_days, max_steps = self._get_avg_price_window()
        sign = -1 if move_type == "out_invoice" else 1
        for step in range(1, max_steps + 1):
            date_from = date_to - timedelta(days=step_days * step)
            groups = self.env["account.move.line"].read_group(
                self._avg_price_domain(products, move_type, date_from, date_to),
                ["balance:sum", "quantity:sum"],
                [],
            )
            quantity = groups[0]["quantity"] if groups else 0
            if quantity:
                return {
                    prefix: sign * groups[0]["balance"] / quantity,
                    "%s_date_from" % prefix: date_from,
                    "%s_date_to" % prefix: date_to,
                }
        return {
            prefix: 0.0,
            "%s_date_from" % prefix: False,
            "%s_date_to" % prefix: False,
        }

    def _update_avg_prices(self, move_types=None):
        """Store the average prices of ``self`` for the given invoice types."""
        for record in self:
            values = {}
            for move_type in move_types or AVG_PRICE_FIELDS:
                values.update(record._get_avg_price_values(move_type))
            record.write(values)

    def _action_avg_price_move_lines(self, move_type, name):
        """Journal items the stored average of ``move_type`` comes from."""
        self.ensure_one()
        prefix = AVG_PRICE_FIELDS[move_type]
        return {
            "type": "ir.actions.act_window",
            "name": name,
            "res_model": "account.move.line",
            "view_mode": "tree,form",
            "domain": self._avg_price_domain(
                self._avg_price_products(),
                move_type,
                self["%s_date_from" % prefix],
                self["%s_date_to" % prefix],
            ),
            "context": {"create": False, "delete": False},
        }

    def action_view_avg_purchase_price_move_lines(self):
        return self._action_avg_price_move_lines(
            "in_invoice", _("Avg. Purchase Price Journal Items")
        )

    def action_view_avg_sale_price_move_lines(self):
        return self._action_avg_price_move_lines(
            "out_invoice", _("Avg. Sale Price Journal Items")
        )

    def action_update_avg_purchase_price(self):
        """Refresh only the stored avg_purchase_price on demand."""
        self._update_avg_prices(("in_invoice",))

    def action_update_avg_sale_price(self):
        """Refresh only the stored avg_sale_price on demand."""
        self._update_avg_prices(("out_invoice",))
