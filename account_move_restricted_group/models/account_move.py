# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models
from odoo.exceptions import AccessError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def check_access(self, operation):
        """Restrict create, write, unlink operations on account.move
        to users in the 'Invoicing & Accounting' group.
        """
        user = self.env.user
        group = "account.group_account_invoice"

        # Only restrict create, write, unlink operations
        if operation != "read" and not self.env.su and not user.has_group(group):
            raise AccessError(
                _("""
                    You do not have the necessary permissions to perform this operation.
                """)
            )
        # If the operation is 'read' or the user has the group, proceed as normal
        return super().check_access(operation=operation)
