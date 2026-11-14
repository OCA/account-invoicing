## Customer Invoices

1.  Go to *Accounting → Customers → Invoices*.
2.  The **Delivery Status** column shows a coloured badge:
    - 🔵 **Not Delivered** – no delivery picking has been validated yet.
    - 🟡 **Partially Delivered** – at least one unit shipped, remainder outstanding.
    - 🟢 **Fully Delivered** – all invoiced storable quantities have been shipped.
3.  Use the **Filters** menu to filter by delivery state, or **Group By → Delivery Status** to segment the list.
4.  Open any invoice to see the badge inline next to the payment state.

![Customer Invoices Delivery Status](static/description/invoice_delivery_status_list.png)

## Vendor Bills

1.  Go to *Accounting → Vendors → Bills*.
2.  The **Receipt Status** column appears with the same three states (Not / Partially / Fully Received).
3.  Filter by receipt state to identify bills that can be safely released for payment under 3-way matching.

![Vendor Bills Receipt Status](static/description/vendor_bill_receipt_status_list.png)

## Customer Portal

Logged-in portal users can see the **Delivery Status** badge on `/my/invoices` and on each invoice's detail page. No warehouse-internal identifiers are exposed.

## Notes

- Invoices or bills containing **only service products** (or with no linked sales/purchase order) will not show a delivery/receipt status badge.
- The status recomputes automatically whenever the linked order lines' delivered or received quantities change.
