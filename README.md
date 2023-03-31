
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/account-invoicing&target_branch=12.0)
[![Pre-commit Status](https://github.com/OCA/account-invoicing/actions/workflows/pre-commit.yml/badge.svg?branch=12.0)](https://github.com/OCA/account-invoicing/actions/workflows/pre-commit.yml?query=branch%3A12.0)
[![Build Status](https://github.com/OCA/account-invoicing/actions/workflows/test.yml/badge.svg?branch=12.0)](https://github.com/OCA/account-invoicing/actions/workflows/test.yml?query=branch%3A12.0)
[![codecov](https://codecov.io/gh/OCA/account-invoicing/branch/12.0/graph/badge.svg)](https://codecov.io/gh/OCA/account-invoicing)
[![Translation Status](https://translation.odoo-community.org/widgets/account-invoicing-12-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/account-invoicing-12-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Account Invoicing

Account invoicing modules for Odoo

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_billing](account_billing/) | 12.0.1.0.1 | [![Saran440](https://github.com/Saran440.png?size=30px)](https://github.com/Saran440) | Group invoice as billing before payment
[account_debitnote](account_debitnote/) | 12.0.1.0.0 |  | Create debit note from invoice and vendor bill
[account_global_discount](account_global_discount/) | 12.0.1.2.2 |  | Account Global Discount
[account_group_invoice_line](account_group_invoice_line/) | 12.0.1.0.1 |  | Add option to group invoice lines per account
[account_invoice_alternate_payer](account_invoice_alternate_payer/) | 12.0.1.0.1 |  | Set a alternate payor/payee in invoices
[account_invoice_analytic_search](account_invoice_analytic_search/) | 12.0.1.0.0 |  | Search invoices by analytic account or by project manager
[account_invoice_anglo_saxon_no_cogs_deferral](account_invoice_anglo_saxon_no_cogs_deferral/) | 12.0.1.0.0 |  | Invalidates the COGS deferral introduced by the anglo saxon module
[account_invoice_blocking](account_invoice_blocking/) | 12.0.1.0.1 |  | Set a blocking (No Follow-up) flag on invoices
[account_invoice_change_currency](account_invoice_change_currency/) | 12.0.1.1.0 |  | Allows to change currency of Invoice by wizard
[account_invoice_check_total](account_invoice_check_total/) | 12.0.1.1.1 |  | Check if the verification total is equal to the bill's total
[account_invoice_confirm_popup](account_invoice_confirm_popup/) | 12.0.1.0.0 |  | Adds a confirmation popup before validation
[account_invoice_date_due](account_invoice_date_due/) | 12.0.1.1.0 | [![luisg123v](https://github.com/luisg123v.png?size=30px)](https://github.com/luisg123v) | Update Invoice's Due Date
[account_invoice_fiscal_position_update](account_invoice_fiscal_position_update/) | 12.0.1.0.2 |  | Changing the fiscal position of an invoice will auto-update invoice lines
[account_invoice_fix_tax_rounding](account_invoice_fix_tax_rounding/) | 12.0.1.0.0 |  | Fix invoice tax rounding globally
[account_invoice_fixed_discount](account_invoice_fixed_discount/) | 12.0.1.0.1 |  | Allows to apply fixed amount discounts in invoices.
[account_invoice_force_number](account_invoice_force_number/) | 12.0.1.0.0 |  | Allows to force invoice numbering on specific invoices
[account_invoice_line_default_account](account_invoice_line_default_account/) | 12.0.1.0.1 |  | Account Invoice Line Default Account
[account_invoice_line_description](account_invoice_line_description/) | 12.0.1.0.0 |  | Account invoice line description
[account_invoice_line_sequence](account_invoice_line_sequence/) | 12.0.1.1.1 |  | Adds sequence field on invoice lines to manage its order.
[account_invoice_mass_sending](account_invoice_mass_sending/) | 12.0.1.0.0 |  | Account Invoice Mass Sending
[account_invoice_merge](account_invoice_merge/) | 12.0.1.0.3 |  | Merge invoices in draft
[account_invoice_pricelist](account_invoice_pricelist/) | 12.0.1.0.6 |  | Add partner pricelist on invoices
[account_invoice_pricelist_sale](account_invoice_pricelist_sale/) | 12.0.1.0.0 |  | Module to fill pricelist from sales order in invoice.
[account_invoice_recompute_tax](account_invoice_recompute_tax/) | 12.0.1.0.1 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Reset Tax Lines Values
[account_invoice_refund_line_selection](account_invoice_refund_line_selection/) | 12.0.1.0.0 |  | This module allows the user to refund specific lines in a invoice
[account_invoice_refund_link](account_invoice_refund_link/) | 12.0.1.0.0 |  | Link refund invoice with its original invoice
[account_invoice_refund_reason](account_invoice_refund_reason/) | 12.0.1.0.1 | [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Account Invoice Refund Reason.
[account_invoice_reimbursable](account_invoice_reimbursable/) | 12.0.1.0.0 |  | Create the option to add reimbursables on invoices
[account_invoice_repair_link](account_invoice_repair_link/) | 12.0.1.0.0 |  | Adds a link in the invoice to the repair from which it was generated
[account_invoice_search_by_reference](account_invoice_search_by_reference/) | 12.0.1.0.1 |  | Account invoice search by reference
[account_invoice_supplier_date](account_invoice_supplier_date/) | 12.0.1.0.0 |  | Move accounting date in supplier invoice near date invoice
[account_invoice_supplier_ref_reuse](account_invoice_supplier_ref_reuse/) | 12.0.1.0.0 |  | Makes it possible to reuse supplier invoice references
[account_invoice_supplier_ref_unique](account_invoice_supplier_ref_unique/) | 12.0.1.0.0 |  | Checks that supplier invoices are not entered twice
[account_invoice_supplier_self_invoice](account_invoice_supplier_self_invoice/) | 12.0.1.1.0 |  | Purchase Self Invoice
[account_invoice_supplierinfo_update](account_invoice_supplierinfo_update/) | 12.0.1.0.2 |  | In the supplier invoice, automatically updates all products whose unit price on the line is different from the supplier price
[account_invoice_supplierinfo_update_discount](account_invoice_supplierinfo_update_discount/) | 12.0.1.0.0 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | In the supplier invoice, automatically update all products whose discount on the line is different from the supplier discount
[account_invoice_supplierinfo_update_triple_discount](account_invoice_supplierinfo_update_triple_discount/) | 12.0.1.0.0 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | In the supplier invoice, automatically update all products whose discounts on the line is different from the supplier discounts
[account_invoice_tax_note](account_invoice_tax_note/) | 12.0.1.0.0 |  | Print tax notes on customer invoices
[account_invoice_tax_required](account_invoice_tax_required/) | 12.0.1.0.2 |  | This module adds functional a check on invoice to force user to set tax on invoice line.
[account_invoice_tier_validation](account_invoice_tier_validation/) | 12.0.1.0.3 |  | Extends the functionality of Invoice to support a tier validation process.
[account_invoice_tier_validation_approver](account_invoice_tier_validation_approver/) | 12.0.1.0.1 |  | Account Invoice Tier Validation Approver
[account_invoice_tier_validation_forward](account_invoice_tier_validation_forward/) | 12.0.1.0.1 |  | Account Invoice Tier Validation - Forward Option
[account_invoice_transmit_method](account_invoice_transmit_method/) | 12.0.2.0.0 |  | Configure invoice transmit method (email, post, portal, ...)
[account_invoice_transmit_method_substitution_rule](account_invoice_transmit_method_substitution_rule/) | 12.0.1.0.0 |  | This addon allow to set substitution rules for transmit method
[account_invoice_triple_discount](account_invoice_triple_discount/) | 12.0.1.0.1 |  | Manage triple discount on invoice lines
[account_invoice_validation_queued](account_invoice_validation_queued/) | 12.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | Enqueue account invoice validation
[account_invoice_view_payment](account_invoice_view_payment/) | 12.0.1.0.1 |  | Access to the payment from an invoice
[account_menu_invoice_refund](account_menu_invoice_refund/) | 12.0.2.0.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | New invoice menu that combine invoices and refunds
[account_payment_term_extension](account_payment_term_extension/) | 12.0.1.2.2 |  | Adds rounding, months, weeks and multiple payment days properties on payment term lines
[account_portal_hide_invoice](account_portal_hide_invoice/) | 12.0.1.0.0 | [![Khalid-SerpentCS](https://github.com/Khalid-SerpentCS.png?size=30px)](https://github.com/Khalid-SerpentCS) | Hide invoices on customer portal.
[product_supplierinfo_for_customer_invoice](product_supplierinfo_for_customer_invoice/) | 12.0.1.0.0 |  | Based on product_customer_code, this module loads in every account invoice the customer code defined in the product
[purchase_batch_invoicing](purchase_batch_invoicing/) | 12.0.1.2.1 |  | Make invoices for all ready purchase orders
[purchase_stock_picking_return_invoicing](purchase_stock_picking_return_invoicing/) | 12.0.1.1.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) [![MiquelRForgeFlow](https://github.com/MiquelRForgeFlow.png?size=30px)](https://github.com/MiquelRForgeFlow) | Add an option to refund returned pickings
[purchase_stock_picking_return_invoicing_force_invoiced](purchase_stock_picking_return_invoicing_force_invoiced/) | 12.0.1.0.0 | [![jbeficent](https://github.com/jbeficent.png?size=30px)](https://github.com/jbeficent) | Glue module between purchase_force_invoiced and purchase_stock_picking_return_invoicing
[sale_invoice_line_note](sale_invoice_line_note/) | 12.0.1.0.0 |  | Propagate sale order note lines to the invoice
[sale_order_invoicing_grouping_criteria](sale_order_invoicing_grouping_criteria/) | 12.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | Sales order invoicing grouping criteria
[sale_order_invoicing_queued](sale_order_invoicing_queued/) | 12.0.2.0.0 |  | Enqueue sales order invoicing
[sale_timesheet_invoice_description](sale_timesheet_invoice_description/) | 12.0.1.0.1 |  | Add timesheet details in invoice line
[stock_picking_invoicing](stock_picking_invoicing/) | 12.0.3.1.0 |  | Stock Picking Invoicing
[stock_picking_return_refund_option](stock_picking_return_refund_option/) | 12.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Update the refund options in pickings

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
