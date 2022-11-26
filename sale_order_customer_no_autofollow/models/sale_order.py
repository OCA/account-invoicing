from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        if self.get_status_autofollow():
            partner_ids.remove(self.partner_id.id)
        return super(SaleOrder, self).message_subscribe(
            partner_ids, channel_ids, subtype_ids
        )

    @api.model_create_multi
    def create(self, values):
        return super(
            SaleOrder, self.with_context(so_no_autofollow=self.get_status_autofollow()),
        ).create(values)

    def action_confirm(self):
        return super(
            SaleOrder, self.with_context(so_no_autofollow=self.get_status_autofollow()),
        ).action_confirm()

    def action_quotation_send(self):
        return super(
            SaleOrder, self.with_context(so_no_autofollow=self.get_status_autofollow()),
        ).action_quotation_send()

    def get_status_autofollow(self):
        return (
            self.env["ir.config_parameter"].sudo().get_param("so.no_autofollow", False)
        )
