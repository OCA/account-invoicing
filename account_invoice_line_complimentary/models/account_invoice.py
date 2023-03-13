#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoice (models.Model):
    _inherit = 'account.invoice'

    show_complimentary_flag = fields.Boolean(
        help="Allow to have complimentary invoice lines.",
    )

    @api.model
    def invoice_line_move_line_get(self):
        res = super().invoice_line_move_line_get()
        company = self.company_id
        complimentary_account = company.complimentary_account_id
        complimentary_lines = self.invoice_line_ids.filtered('is_complimentary')
        if complimentary_lines and not complimentary_account:
            raise UserError(
                _("Invoice Lines {lines} are set as complimentary "
                  "but there is not Complimentary Account set in Company {company}.\n"
                  "Please set the Complimentary Account.")
                .format(
                    lines=', '.join(
                        complimentary_lines.mapped('display_name')),
                    company=company.display_name,
                )
            )

        # Add a new Journal Item for each Complimentary Line
        for line in complimentary_lines:
            move_line_values = list(filter(
                lambda ml_values: ml_values.get('invl_id') == line.id,
                res,
            ))
            if move_line_values:
                move_line_values = move_line_values[0]

                # Copy the values of the existing Journal Item
                # for this Invoice line in order to preserve
                # fields added by other modules, only overwrite what we need
                complimentary_line_values = move_line_values.copy()
                complimentary_line_values.update({
                    'account_id': complimentary_account.id,
                    'tax_ids': False,
                    'price': -line.price_total,
                })
                res.append(complimentary_line_values)
        return res
