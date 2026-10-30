If 'Stock Picking' is chosen as Policy, the creation of Invoice from
Sale Order works only for Service lines. In the case of Sale Order with
products and service lines, two Invoices will be created (one from the
SO with services, one from the picking with products).

If 'Sale Order and Stock Picking' is chosen, invoices can be created
from both the Sale Order and the Stock Picking. When invoicing from the
Sale Order, the related picking invoice state is automatically synced.
The picking wizard prevents double invoicing by capping quantities to
what remains to invoice on the sale line.
