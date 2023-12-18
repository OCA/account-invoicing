This module allows to select a `At shipping` invoicing mode for a customer.
It is based on `partner_invoicing_mode`.
When this mode is selected the customer will be invoiced automatically on
delivery of the goods.

Another option is the 'One Invoice Per Shipping'. That one is not compatible
with the 'At shipping' invoicing mode. In that case, the invoicing validation
will occur at a different moment (monthly, ...).
