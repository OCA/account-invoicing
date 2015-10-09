[![Build Status](https://travis-ci.org/OCA/account-invoicing.svg?branch=8.0)](https://travis-ci.org/OCA/account-invoicing)
[![Coverage Status](https://coveralls.io/repos/OCA/account-invoicing/badge.svg?branch=8.0)](https://coveralls.io/r/OCA/account-invoicing?branch=8.0)

OCA account invoicing modules for Odoo
======================================

This project aim to deal with modules related to manage invoicing in a generic way. You'll find modules that:

 - Add a validation step on invoicing process
 - Add check on invoice
 - Unit rounded invoice
 - Utils and ease of use for invoicing with OpenERP
 - ...

[//]: # (addons)
Available addons
----------------
addon | version | summary
--- | --- | ---
[account_group_invoice_lines](account_group_invoice_lines/) | 8.0.1.1.0 | Add option to group invoice line per account
[account_invoice_force_number](account_invoice_force_number/) | 8.0.0.1.0 | Allows to force invoice numbering on specific invoices
[account_invoice_line_description](account_invoice_line_description/) | 8.0.1.0.0 | Account invoice line description
[account_invoice_line_sort](account_invoice_line_sort/) | 8.0.0.1.0 | Manage sort of customer invoice lines by customers
[account_invoice_merge](account_invoice_merge/) | 8.0.1.1.1 | Account Invoice Merge Wizard
[account_invoice_merge_payment](account_invoice_merge_payment/) | 8.0.0.1.0 | Use invoice merge regarding fields on Account Payment Partner
[account_invoice_merge_purchase](account_invoice_merge_purchase/) | 8.0.1.0.0 | Compatibility between purchase and account invoice merge
[account_invoice_partner](account_invoice_partner/) | 8.0.0.2.0 | Automatically select invoicing partner on invoice
[account_invoice_period_usability](account_invoice_period_usability/) | 8.0.1.0.0 | Display in the supplier invoice form the fiscal period next to the invoice date
[account_invoice_pricelist](account_invoice_pricelist/) | 8.0.1.0.0 | Add partner pricelist on invoices
[account_invoice_rounding](account_invoice_rounding/) | 8.0.1.0.0 | Unit rounded invoice
[account_invoice_shipping_address](account_invoice_shipping_address/) | 8.0.0.1.1 | Adds a shipping address field to the invoice.
[account_invoice_supplier_ref_unique](account_invoice_supplier_ref_unique/) | 8.0.1.1.0 | Checks that supplier invoices are not entered twice
[account_invoice_uom](account_invoice_uom/) | 8.0.1.0.0 | Unit of measure for invoices
[account_invoice_validation_workflow](account_invoice_validation_workflow/) | 8.0.1.0.0 | Add "To Send" and "To Validate" states in Invoices
[account_invoice_zero_autopay](account_invoice_zero_autopay/) | 8.0.1.0.0 | Account Invoice Zero Autopay
[account_payment_term_extension](account_payment_term_extension/) | 8.0.1.0.0 | Adds rounding, months and weeks properties on payment term lines
[invoice_fiscal_position_update](invoice_fiscal_position_update/) | 8.0.1.0.0 | Changing the fiscal position of an invoice will auto-update invoice lines
[stock_picking_invoicing](stock_picking_invoicing/) | 8.0.1.0.0 | Stock Picking Invoicing

Unported addons
---------------
addon | version | summary
--- | --- | ---
[account_invoice_customer_ref_unique](__unported__/account_invoice_customer_ref_unique/) | 1.0 (unported) | Unique Customer Reference in Invoice
[account_invoice_template](__unported__/account_invoice_template/) | 0.1 (unported) | Account Invoice Template
[product_customer_code_invoice](__unported__/product_customer_code_invoice/) | 1.0 (unported) | Product Customer code for account invoice
[sale_order_partial_invoice](__unported__/sale_order_partial_invoice/) | 1.1 (unported) | Sale Partial Invoice
[stock_invoice_picking_incoterm](__unported__/stock_invoice_picking_incoterm/) | 0.1 (unported) | Stock Invoice Picking Incoterm

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-account-invoicing-8-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-account-invoicing-8-0)

----

OCA, or the Odoo Community Association, is a nonprofit organization whose 
mission is to support the collaborative development of Odoo features and 
promote its widespread use.

http://odoo-community.org/
