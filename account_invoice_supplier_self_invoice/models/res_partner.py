# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo import _, exceptions, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    self_invoice = fields.Boolean(
        string="Approves Self Billing",
        default=False,
        help="When checked, all vendor Bills will generate by default "
        "a Self-Bill Invoice on confirmation.",
        tracking=True,
        copy=False,
        company_dependent=True,
    )
    self_invoice_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Self Billing sequence",
        ondelete="restrict",
        groups="base.group_no_one",
        copy=False,
        company_dependent=True,
    )
    self_invoice_report_footer = fields.Text(
        string="Self Billing footer",
        default="Invoiced by the recipient",
        help="Footer text displayed at the bottom of the self invoice reports.",
        copy=False,
        tracking=True,
        company_dependent=True,
    )

    def _get_self_invoice_number(self, date):
        sequence = self.self_invoice_sequence_id
        if not sequence:
            sequence = self._set_self_invoice()
        return sequence.sudo().with_context(ir_sequence_date=date).next_by_id()

    def _set_self_invoice(self):
        if not self.self_invoice:
            return False
        if not self.self_invoice_sequence_id:
            self.sudo().self_invoice_sequence_id = (
                self.env["ir.sequence"]
                .sudo()
                .create(
                    {
                        "name": self.name + " Self invoice sequence",
                        "implementation": "no_gap",
                        "number_increment": 1,
                        "padding": 4,
                        "prefix": self._self_invoice_sequence_prefix(),
                        "use_date_range": True,
                        "number_next": 1,
                    }
                )
            )
        return self.self_invoice_sequence_id

    def _self_invoice_sequence_prefix(self):
        self.ensure_one()
        if not self.env.company.self_invoice_prefix:
            raise exceptions.UserError(
                _("You must set a Self Billing prefix in Account Settings.")
            )
        first_prefix = self.env.company.self_invoice_prefix
        second_prefix = (self.ref or "").strip().upper() or "SI"
        return f"{first_prefix}/{second_prefix}/INV/%(range_year)s/"
