from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(
        # Added before "Down payment (percentage)" option
        selection_add=[
            ("qty_percentage", "Percentage of the quantity"),
            ("percentage",),
        ],
        ondelete={"qty_percentage": "set default"},
    )
    qty_percentage = fields.Float(string="Quantity percentage")

    def create_invoices(self):
        """Inject context key for later use that information to modify quantities
        and switch the invoiced method back to regular one for using the normal flow.
        """
        if self.advance_payment_method == "qty_percentage":
            self = self.with_context(qty_percentage=self.qty_percentage)
            self.advance_payment_method = "delivered"
        return super().create_invoices()
