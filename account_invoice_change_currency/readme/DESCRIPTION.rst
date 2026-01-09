==================================
Update currency of Account Invoice
==================================

This module allows users to update the currency of Invoices (in draft state) by
a button Update Currency at the invoice form.
After update to new currency, all the unit prices of invoice lines will be
recomputed to new currency, thus the Total amounts (tax and without tax) of
Invoice will be in the new currency also

Also this module allows user to set a custom rate that will be take to recompute
all lines. By default the custom rate proposed is the rate between invoice
currency and base currency (company currency), after the first coversion the
custom rate will be proposed by default between last currency and invoice
currency.
