[![Build Status](https://travis-ci.org/OCA/account-invoicing.svg?branch=9.0)](https://travis-ci.org/OCA/account-invoicing)
[![Coverage Status](https://coveralls.io/repos/OCA/account-invoicing/badge.svg?branch=9.0)](https://coveralls.io/r/OCA/account-invoicing?branch=9.0)

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
[account_invoice_blocking](account_invoice_blocking/) | 9.0.1.0.0 | This module allows the user to set a blocking (No Follow-up) flag on invoices.
[account_invoice_check_total](account_invoice_check_total/) | 9.0.1.0.0 | Check if the verification total is equal to the bill's total
[account_invoice_fiscal_position_update](account_invoice_fiscal_position_update/) | 9.0.1.0.0 | Changing the fiscal position of an invoice will auto-update invoice lines
[account_invoice_line_sequence](account_invoice_line_sequence/) | 9.0.1.0.0 | Adds sequence field on invoice lines to manage its order.
[account_invoice_merge](account_invoice_merge/) | 9.0.1.0.1 | Account Invoice Merge Wizard
[account_invoice_merge_payment](account_invoice_merge_payment/) | 9.0.1.0.0 | Use invoice merge regarding fields on Account Payment Partner
[account_invoice_merge_purchase](account_invoice_merge_purchase/) | 9.0.1.0.0 | Compatibility between purchase and account invoice merge
[account_invoice_pricelist](account_invoice_pricelist/) | 9.0.1.0.0 | Add partner pricelist on invoices
[account_invoice_refund_link](account_invoice_refund_link/) | 9.0.2.0.2 | Link refund invoice with its original invoice
[account_invoice_refund_option](account_invoice_refund_option/) | 9.0.1.0.0 | Allows you to create directly a refund without starting from an invoice
[account_invoice_rounding](account_invoice_rounding/) | 9.0.1.0.1 | Unit rounded invoice
[account_invoice_search_by_reference](account_invoice_search_by_reference/) | 9.0.1.0.0 | Account invoice search by reference
[account_invoice_supplier_ref_unique](account_invoice_supplier_ref_unique/) | 9.0.1.0.0 | Checks that supplier invoices are not entered twice
[account_invoice_view_payment](account_invoice_view_payment/) | 9.0.1.0.0 | Access to the payment from an invoice
[account_payment_term_extension](account_payment_term_extension/) | 9.0.1.0.0 | Adds rounding, months, weeks and multiple payment days properties on payment term lines
[purchase_batch_invoicing](purchase_batch_invoicing/) | 9.0.1.0.0 | Make invoices for all ready purchase orders
[purchase_stock_picking_return_invoicing](purchase_stock_picking_return_invoicing/) | 9.0.1.1.0 | Add an option to refund returned pickings
[purchase_stock_picking_return_invoicing_open_qty](purchase_stock_picking_return_invoicing_open_qty/) | 9.0.1.0.0 | This a glue module to combine two modules
[sale_stock_picking_return_invoicing](sale_stock_picking_return_invoicing/) | 9.0.1.0.0 | Add an option to refund return pickings
[sale_timesheet_invoice_description](sale_timesheet_invoice_description/) | 9.0.1.0.0 | Add timesheet details in invoice line


Unported addons
---------------
addon | version | summary
--- | --- | ---
[account_group_invoice_lines](account_group_invoice_lines/) | 8.0.1.1.0 (unported) | Add option to group invoice line per account
[account_invoice_customer_ref_unique](account_invoice_customer_ref_unique/) | 1.0 (unported) | Unique Customer Reference in Invoice
[account_invoice_force_number](account_invoice_force_number/) | 8.0.0.1.0 (unported) | Allows to force invoice numbering on specific invoices
[account_invoice_line_description](account_invoice_line_description/) | 8.0.1.0.0 (unported) | Account invoice line description
[account_invoice_line_sort](account_invoice_line_sort/) | 8.0.0.1.0 (unported) | Manage sort of customer invoice lines by customers
[account_invoice_partner](account_invoice_partner/) | 8.0.0.2.0 (unported) | Automatically select invoicing partner on invoice
[account_invoice_period_usability](account_invoice_period_usability/) | 8.0.1.0.0 (unported) | Display in the supplier invoice form the fiscal period next to the invoice date
[account_invoice_shipping_address](account_invoice_shipping_address/) | 8.0.0.1.1 (unported) | Adds a shipping address field to the invoice.
[account_invoice_template](account_invoice_template/) | 0.1 (unported) | Account Invoice Template
[account_invoice_uom](account_invoice_uom/) | 8.0.1.0.0 (unported) | Unit of measure for invoices
[account_invoice_validation_workflow](account_invoice_validation_workflow/) | 8.0.1.0.1 (unported) | Add "To Send" and "To Validate" states in Invoices
[account_invoice_zero_autopay](account_invoice_zero_autopay/) | 8.0.1.0.0 (unported) | Account Invoice Zero Autopay
[product_customer_code_invoice](product_customer_code_invoice/) | 1.0 (unported) | Product Customer code for account invoice
[sale_order_partial_invoice](sale_order_partial_invoice/) | 1.1 (unported) | Sale Partial Invoice
[stock_invoice_picking_incoterm](stock_invoice_picking_incoterm/) | 0.1 (unported) | Stock Invoice Picking Incoterm
[stock_picking_invoicing](stock_picking_invoicing/) | 8.0.1.0.0 (unported) | Stock Picking Invoicing

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-account-invoicing-9-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-account-invoicing-9-0)

----

OCA, or the Odoo Community Association, is a nonprofit organization whose 
mission is to support the collaborative development of Odoo features and 
promote its widespread use.

http://odoo-community.org/
