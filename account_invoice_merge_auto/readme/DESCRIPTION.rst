This module implements automatic merge of invoices.

A cron entry is used to regularly merge invoices that are draft and
which `Merge automatically` attribute is True. This requires the invoice partner
to have attributes set that define the recurring automatic merge date.

The invoices are merged together according to rules defined in the
`account_invoice_merge` module. The candidate invoices are returned
whatever they were effectively removed or not. Invoices that were
created as the result of a merge have their invoice date set to the
merge date (that is the execution date of the cron task, by default).
