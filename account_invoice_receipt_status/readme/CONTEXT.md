In Odoo, when vendor bills are generated from purchase orders, the financial
review of an invoice frequently requires understanding where the reception
process stands.

More and more frequently — especially with the adoption of electronic
invoicing networks such as Peppol — vendor invoices may arrive *before* the
physical goods are received. This makes it very difficult for the accounting
team to determine when the invoice can be processed or approved for payment.

The OCA module `purchase_line_receipt_status` provides a reception status at
the purchase order line level, based on the picking workflow, without relying
on quantities.

This module complements `purchase_line_receipt_status` by propagating this
reception status to the vendor bill line, so that the invoice reviewer has the
same information available where the invoice is processed.