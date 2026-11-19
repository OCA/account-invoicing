# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class ValidateAccountMove(models.TransientModel):
    _inherit = "validate.account.move"

    def validate_move(self):
        # Moves posted through this wizard (e.g. "Confirm Entries" when the
        # amount or date of a bill is considered abnormal) call ``_post()``
        # directly instead of ``action_post()``. Pass the same context as
        # ``account.move.action_post()`` so the fields written while posting
        # (e.g. ``checked``) are not blocked as writes under validation.
        # Posting a move whose validation is not finished stays blocked.
        return super(
            ValidateAccountMove, self.with_context(skip_validation_check=True)
        ).validate_move()
