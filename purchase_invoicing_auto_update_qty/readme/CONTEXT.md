In standard Odoo, when a vendor bill is created from a purchase order before product reception, the invoice lines are initialized with the `qty_to_invoice` value from the purchase order lines at that moment. 

If subsequent receptions occur, the `qty_to_invoice` on the purchase order lines increases, but existing draft invoices are not automatically updated. This can result in draft vendor bills having quantities that are outdated and do not reflect the actual receivable amounts.

Practical examples:

- A company receives goods in multiple shipments. A draft vendor bill was created before all goods arrived. Without updating the draft invoice, the invoice will under-report the quantities to be billed.
- In electronic invoicing scenarios such as Peppol, draft invoices may be created early in the process, requiring them to reflect new received quantities automatically.

This module addresses the issue by detecting changes in the `qty_to_invoice` on purchase order lines. When the `qty_to_invoice` is updated, it checks for related draft invoice lines and adds the updated quantities to them. Then, it invalidates the `qty_to_invoice` field to ensure that the changes are reflected in the user interface and avoid double counting.

This ensures that draft invoices always reflect the latest quantities available to bill, without requiring manual intervention.
