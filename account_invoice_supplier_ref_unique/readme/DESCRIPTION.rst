This module checks that a supplier invoice/refund is not entered twice. This is important because if you enter twice the same supplier invoice, there is also a risk that you pay it twice !

This module adds a constraint on supplier invoice/refunds to check that (commercial_partner_id, supplier_invoice_number) is unique, without considering the case of the supplier invoice number.
