This module checks that a customer invoice/refund is not entered twice. This is important because if you enter twice the same customer invoice, there is also a risk that they pay it twice !

This module adds a constraint on customer invoice/refunds to check that (commercial_partner_id, customer_invoice_number) is unique, without considering the case of the customer invoice number.
