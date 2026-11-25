This module restricts the partner selection on invoices to companies only.
When selecting a partner on an invoice, only partners marked as companies
(is_company = True) will be available in the selection list.

This module is used by ``sale_partner_sale_contact`` (available in the
sale-workflow repository) to enforce proper commercial relationships while
allowing contact person tracking.
