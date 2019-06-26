# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    billing_id = fields.Many2one(
        comodel_name='account.billing',
        string='Billing',
        copy=False,
        index=True,
        readonly=True,
        help="Relationship between invoice and billing"
    )
