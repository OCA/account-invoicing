This module adds a warning banner on the customer form view when it has overdue invoices. The banner informs the user about the number of overdue invoices and the total overdue amount. It contains a link to see the corresponding overdue invoices.

.. figure:: static/description/partner_overdue_invoice_warn.png
   :scale: 80 %
   :alt: Screenshot of partner form view

If you also install the module *account_invoice_overdue_warn_sale*, you will have the same banner on the form view of quotations and sale orders.

Implementation details:

* in a multi-company configuration, the overdue invoices taken into account are the invoices of the company of the partner, or, if the partner is not attached to a company, in the current company.
* the overdue amount is in the company currency.
* the overdue banner is displayed on the parent partner and also all its contacts. The overdue invoices taken into account are all the overdue invoices of the parent partners and all its contacts.
