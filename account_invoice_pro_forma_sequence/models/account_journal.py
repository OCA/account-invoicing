from odoo import _, api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    pro_forma_sequence_id = fields.Many2one(
        "ir.sequence", string="Pro-forma Sequence", required=False, copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        journal = super(AccountJournal, self).create(vals_list)
        if journal.type == "sale":
            journal._set_pro_forma_sequence_id()
        return journal

    def _set_pro_forma_sequence_id(self):
        journal_vals = self.read()[0]
        if not journal_vals.get("pro_forma_sequence_id"):
            self.sudo()._create_secure_sequence(["pro_forma_sequence_id"])
            seq = self.pro_forma_sequence_id
            seq.name = _("PRO-FORMA %s") % seq.name
            seq.prefix = _("PRO-FORMA %s") % seq.prefix
            self.pro_forma_sequence_id = seq.id
