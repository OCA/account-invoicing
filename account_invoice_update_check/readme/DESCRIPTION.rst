Natively, in odoo, it is possible to write on account invoice lines, even if the invoices are validated.
It is possible via ORM, or via extra UI tools.

This module implement a check when writing on account invoice lines, to avoid such possibility.

The implementation is similar to the ``update_check`` function implemented in native odoo, for the
``account.move.line`` models.
