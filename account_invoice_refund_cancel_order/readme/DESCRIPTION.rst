This module acts when cancelling a sale order:
* If cancelled sale order has a draft invoices: Cancels them
* If cancelled sale order has a opened invoice: Creates a refund order and reconcile with opened invoice
* If cancelled sale order has a paid invoice: Creates a refund order and pay it
