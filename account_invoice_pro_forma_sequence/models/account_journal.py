from odoo import _, api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    pro_forma_sequence_id = fields.Many2one(
        "ir.sequence", string="Pro-forma Sequence", copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        journals = super().create(vals_list)
        for journal in journals:
            if journal.type == "sale":
                journal._set_pro_forma_sequence_id()
        return journals

    def _set_pro_forma_sequence_id(self):
        for journal in self:
            if not journal.pro_forma_sequence_id:
                seq = (
                    self.env["ir.sequence"]
                    .sudo()
                    .create(
                        {
                            "name": _("PRO-FORMA %s") % journal.name,
                            "code": "pro_forma-%s" % journal.id,
                            "prefix": "PRO-FORMA ",
                            "padding": 4,
                            "company_id": journal.company_id.id,
                        }
                    )
                )
                journal.pro_forma_sequence_id = seq
