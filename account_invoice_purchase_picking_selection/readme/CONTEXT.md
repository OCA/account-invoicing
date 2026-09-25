When creating a vendor bill from a purchase order, Odoo currently imports all
purchase order lines into the invoice.

This becomes impractical when a purchase order is received through multiple
deliveries and the accounting department creates supplier invoices separately
for each reception.

With the standard Odoo behavior based on received quantities, the vendor bill
includes all quantities received so far on the purchase order, regardless of
which reception they belong to.

However, some suppliers issue one invoice per delivery. In these cases,
users need to create a vendor bill linked to a specific reception only.

As a result, users currently have to manually remove unrelated lines and adjust
quantities, which is both time-consuming and error-prone.
