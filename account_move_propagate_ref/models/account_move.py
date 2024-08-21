# Copyright 2021 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def copy_data(self, default=None):
        """Add `ref` to copied fields

        The same feature could've been achieved by setting `copy=True` in
        the field's definition, but it would've made the field copiable
        everywhere.
        Instead, we just need to copy it when reversing a move and creating a
        new one from it, which is done by calling :meth:`copy_data`.
        """
        self.ensure_one()
        if self.env.context.get("propagate_ref"):
            default = dict(default or [])
            # Avoid overwriting existing ref; for example, on reversal moves,
            # it's ok have "Reversal of: <MOVENAME>", but when creating a new
            # draft move, "ref" will be missing from `default`
            if "ref" not in default and self.ref:
                default["ref"] = self.ref
        return super().copy_data(default)
