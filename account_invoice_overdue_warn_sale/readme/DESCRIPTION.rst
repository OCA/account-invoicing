This module adds a warning banner on quotation and sale order form view when the invoicing partner has overdue invoices. The banner informs the user about the number of overdue invoices and the total overdue amount. It contains a link to see the corresponding overdue invoices.

.. figure:: static/description/sale_order_overdue_invoice_warn.png
   :scale: 80 %
   :alt: Screenshot of partner form view

This module depends on the module *account_invoice_overdue_warn* which adds the same banner on the form view of partners.

Implementation details:

* in a multi-company configuration, the overdue invoices taken into account are the invoices of the company of the sale order.
* the overdue amount is in the company currency.
* the overdue invoices taken into account are all the overdue invoices of the parent partner of the invoicing partner of the order and of all its contacts.
