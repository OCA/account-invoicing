When creating credit notes for sale or purchase invoices, Odoo will reset the
invoiced quantities on the order lines and make the orders become eligible for
invoicing again. This module adds a checkbox in the credit note (or 'reversal')
wizard to keep the invoiced quantities on the related order lines.

This module takes special care to ensure that these 'dangling' reversals are
still accessible when navigating from sale or purchase orders to their linked
invoices.
