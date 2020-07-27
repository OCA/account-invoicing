# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        domain=[('model_id.model', '=', 'account.invoice')],
        string='Invoice mail template id'
    )
    invoice_mail_author_id = fields.Many2one(
        comodel_name='res.users',
        string='Invoice mail template author id'
    )
    invoice_mail_days = fields.Integer(
        string='Invoice mail days'
    )
