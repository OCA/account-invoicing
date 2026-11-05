This module adds **Delivery Status** and **Receipt Status** fields to
customer invoices and vendor bills, giving accounting teams real-time
visibility into how much of each invoice is backed by validated stock
movements.

- **Customer Invoices** display a `Delivery Status` badge: *Not Delivered*,
  *Partially Delivered*, or *Fully Delivered*, computed from the linked
  sales order lines' delivered quantities.
- **Vendor Bills** display a `Receipt Status` badge: *Not Received*,
  *Partially Received*, or *Fully Received*, computed from the linked
  purchase order lines' received quantities.
- Status is `False` (badge hidden) for invoices/bills that contain only
  service products or have no source order, avoiding noise for non-stock
  transactions.
- Both fields are **stored and indexed**, making them searchable and
  groupable in list views and via the ORM.
- A **Delivery Status** column is also available on the customer portal
  (`/my/invoices`) so customers can track fulfilment alongside payment.
