This module ensures that only one VAT tax can be selected because
the invoices (at least in Belgium) must have one and only one
VAT tax per line. So this module comes to complete the OCA module
account_invoice_tax_required which ensures a line has a tax.
It deals with taxes on these objects:
* account move line (onchange warning only)
* product template for both customer and supplier (constraint only)

The module adds two computed fields on product - vat_id and
vat (vat_id.name) - which might be set if the restriction is on.

It also adds a boolean field in the account.tax model to indicates the
tax is a VAT.
