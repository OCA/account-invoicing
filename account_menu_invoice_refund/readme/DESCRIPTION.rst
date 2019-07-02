By Odoo standard, Invoices and Refunds are in different menu,
and can't be mixed upon payment.

This module add 2 new menus,

1. Invoicing > Customers > Invoices / Credit Notes
2. Invoicing > Vendors > Bills / Refunds

Additionally it allow register net payment by selecting both invoice and refund.

**Note:**
This is accomplished by simply remove the condition that disallow
mixing invoice and refund in account.payment's default_get()
