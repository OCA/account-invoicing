[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/95/13.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-account-invoicing-95)
[![Build Status](https://travis-ci.org/OCA/account-invoicing.svg?branch=13.0)](https://travis-ci.org/OCA/account-invoicing)
[![Coverage Status](https://coveralls.io/repos/OCA/account-invoicing/badge.svg?branch=13.0)](https://coveralls.io/r/OCA/account-invoicing?branch=13.0)

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
addon | version | maintainers | summary
--- | --- | --- | ---
[account_billing](account_billing/) | 13.0.1.0.3 | [![Saran440](https://github.com/Saran440.png?size=30px)](https://github.com/Saran440) | Group invoice as billing before payment
[account_global_discount](account_global_discount/) | 13.0.2.0.1 |  | Account Global Discount
[account_invoice_base_invoicing_mode](account_invoice_base_invoicing_mode/) | 13.0.1.0.1 |  | Base module for handling multiple invoicing mode
[account_invoice_check_total](account_invoice_check_total/) | 13.0.1.0.0 |  | Check if the verification total is equal to the bill's total
[account_invoice_date_due](account_invoice_date_due/) | 13.0.1.0.1 | [![luisg123v](https://github.com/luisg123v.png?size=30px)](https://github.com/luisg123v) [![joao-p-marques](https://github.com/joao-p-marques.png?size=30px)](https://github.com/joao-p-marques) | Update Invoice's Due Date
[account_invoice_fiscal_position_update](account_invoice_fiscal_position_update/) | 13.0.1.0.3 |  | Changing the fiscal position of an invoice will auto-update invoice lines
[account_invoice_fixed_discount](account_invoice_fixed_discount/) | 13.0.1.0.2 |  | Allows to apply fixed amount discounts in invoices.
[account_invoice_force_number](account_invoice_force_number/) | 13.0.1.0.0 |  | Allows to force invoice numbering on specific invoices
[account_invoice_mode_at_shipping](account_invoice_mode_at_shipping/) | 13.0.1.0.1 |  | Create invoices automatically when goods are shipped.
[account_invoice_mode_monthly](account_invoice_mode_monthly/) | 13.0.1.0.1 |  | Create invoices automatically on a monthly basis.
[account_invoice_pricelist](account_invoice_pricelist/) | 13.0.1.0.2 |  | Add partner pricelist on invoices
[account_invoice_pricelist_sale](account_invoice_pricelist_sale/) | 13.0.1.0.1 |  | Module to fill pricelist from sales order in invoice.
[account_invoice_refund_line_selection](account_invoice_refund_line_selection/) | 13.0.1.0.0 |  | This module allows the user to refund specific lines in a invoice
[account_invoice_refund_link](account_invoice_refund_link/) | 13.0.1.1.0 |  | Show links between refunds and their originator invoices
[account_invoice_search_by_reference](account_invoice_search_by_reference/) | 13.0.1.0.0 |  | Account invoice search by reference
[account_invoice_section_sale_order](account_invoice_section_sale_order/) | 13.0.1.0.0 |  | For invoices targetting multiple sale order addsections with sale order name.
[account_invoice_show_currency_rate](account_invoice_show_currency_rate/) | 13.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Show currency rate in invoices.
[account_invoice_supplier_ref_reuse](account_invoice_supplier_ref_reuse/) | 13.0.1.0.0 |  | Makes it possible to reuse supplier invoice references
[account_invoice_supplier_ref_unique](account_invoice_supplier_ref_unique/) | 13.0.1.0.3 |  | Checks that supplier invoices are not entered twice
[account_invoice_supplier_self_invoice](account_invoice_supplier_self_invoice/) | 13.0.1.1.0 |  | Purchase Self Invoice
[account_invoice_tax_note](account_invoice_tax_note/) | 13.0.1.0.0 |  | Print tax notes on customer invoices
[account_invoice_tax_required](account_invoice_tax_required/) | 13.0.1.0.1 |  | This module adds functional a check on invoice to force user to set tax on invoice line.
[account_invoice_transmit_method](account_invoice_transmit_method/) | 13.0.1.1.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Configure invoice transmit method (email, post, portal, ...)
[account_invoice_tree_currency](account_invoice_tree_currency/) | 13.0.1.0.0 |  | Show currencies in the invoice tree view
[account_invoice_validation_queued](account_invoice_validation_queued/) | 13.0.2.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | Enqueue account invoice validation
[account_invoice_warn_message](account_invoice_warn_message/) | 13.0.1.0.0 |  | Add a popup warning on invoice to ensure warning is populated
[account_menu_invoice_refund](account_menu_invoice_refund/) | 13.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | New invoice menu that combine invoices and refunds
[account_move_exception](account_move_exception/) | 13.0.1.0.1 |  | Custom exceptions on account move
[account_move_post_block](account_move_post_block/) | 13.0.1.0.2 |  | Account Move Post Block
[account_move_tier_validation](account_move_tier_validation/) | 13.0.1.0.4 |  | Extends the functionality of Account Moves to support a tier validation process.
[account_move_tier_validation_approver](account_move_tier_validation_approver/) | 13.0.1.0.0 |  | Account Move Tier Validation Approver
[account_tax_group_widget_base_amount](account_tax_group_widget_base_amount/) | 13.0.1.0.0 | [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) | Adds base to tax group widget as it's put in the report
[product_supplierinfo_for_customer_invoice](product_supplierinfo_for_customer_invoice/) | 13.0.1.0.0 |  | Based on product_customer_code, this module loads in every account invoice the customer code defined in the product
[purchase_batch_invoicing](purchase_batch_invoicing/) | 13.0.1.0.1 |  | Make invoices for all ready purchase orders
[purchase_stock_picking_return_invoicing](purchase_stock_picking_return_invoicing/) | 13.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | Add an option to refund returned pickings
[sale_line_refund_to_invoice_qty](sale_line_refund_to_invoice_qty/) | 13.0.1.2.0 |  | Allow deciding whether refunded quantity should be considered as quantity to reinvoice
[sale_order_invoicing_grouping_criteria](sale_order_invoicing_grouping_criteria/) | 13.0.2.0.2 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | Sales order invoicing grouping criteria
[sale_order_invoicing_queued](sale_order_invoicing_queued/) | 13.0.2.0.1 |  | Enqueue sales order invoicing
[sale_timesheet_invoice_description](sale_timesheet_invoice_description/) | 13.0.1.0.0 |  | Add timesheet details in invoice line
[stock_picking_return_refund_option](stock_picking_return_refund_option/) | 13.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Update the refund options in pickings

[//]: # (end addons)

Translation Status
------------------

[![Translation status](https://translation.odoo-community.org/widgets/account-invoicing-13-0/-/multi-auto.svg)](https://translation.odoo-community.org/engage/account-invoicing-13-0/?utm_source=widget)

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.
