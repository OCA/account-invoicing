Allow to revert a credit note. Standard Odoo does not allow it.
When reverting the credit note from the journal entry Standard Odoo
does not link it to the Sales order, because the reversal is not an
invoice. This module just ensure the reveral is a customer invoice,
so it counts as invoice in the sales order.

This also serves when the posting credit notes by mistake. For example,
when adding a negative quantity in the sale line and creating Odoo will
actually create a credit note, then, if other lines with positive quantites
are added nothing changes, and the invoice will be still a credit note.
