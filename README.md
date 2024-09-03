
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/account-invoicing&target_branch=16.0)
[![Pre-commit Status](https://github.com/OCA/account-invoicing/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/OCA/account-invoicing/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/OCA/account-invoicing/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/OCA/account-invoicing/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/OCA/account-invoicing/branch/16.0/graph/badge.svg)](https://codecov.io/gh/OCA/account-invoicing)
[![Translation Status](https://translation.odoo-community.org/widgets/account-invoicing-16-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/account-invoicing-16-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# account-invoicing

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_global_discount](account_global_discount/) | 16.0.1.0.1 |  | Account Global Discount
[account_invoice_alternate_payer](account_invoice_alternate_payer/) | 16.0.1.0.0 |  | Set a alternate payor/payee in invoices
[account_invoice_block_payment](account_invoice_block_payment/) | 16.0.1.0.0 |  | Module to block payment of invoices
[account_invoice_blocking](account_invoice_blocking/) | 16.0.1.0.1 |  | Set a blocking (No Follow-up) flag on invoices
[account_invoice_change_currency](account_invoice_change_currency/) | 16.0.1.0.1 | [![luisg123v](https://github.com/luisg123v.png?size=30px)](https://github.com/luisg123v) [![rolandojduartem](https://github.com/rolandojduartem.png?size=30px)](https://github.com/rolandojduartem) | Allows to change currency of Invoice by wizard
[account_invoice_check_total](account_invoice_check_total/) | 16.0.1.0.0 |  | Check if the verification total is equal to the bill's total
[account_invoice_crm_tag](account_invoice_crm_tag/) | 16.0.1.0.0 |  | Account Invoice CRM Tag
[account_invoice_currency_taxes](account_invoice_currency_taxes/) | 16.0.1.0.2 |  | Taxes in company currency in invoice report
[account_invoice_default_code_column](account_invoice_default_code_column/) | 16.0.1.0.0 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Display Default code product in a dedicated column on invoice reports
[account_invoice_discount_display_amount](account_invoice_discount_display_amount/) | 16.0.1.1.0 |  | Show total discount applied and total without discount on invoices.
[account_invoice_fiscal_position_update](account_invoice_fiscal_position_update/) | 16.0.1.0.1 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Changing the fiscal position of an invoice will auto-update invoice lines
[account_invoice_fixed_discount](account_invoice_fixed_discount/) | 16.0.1.0.4 |  | Allows to apply fixed amount discounts in invoices.
[account_invoice_force_number](account_invoice_force_number/) | 16.0.1.0.1 |  | Allows to force invoice numbering on specific invoices
[account_invoice_line_default_account](account_invoice_line_default_account/) | 16.0.1.0.0 |  | Account Invoice Line Default Account
[account_invoice_mass_sending](account_invoice_mass_sending/) | 16.0.1.1.1 | [![jguenat](https://github.com/jguenat.png?size=30px)](https://github.com/jguenat) | This addon adds a mass sending feature on invoices.
[account_invoice_merge](account_invoice_merge/) | 16.0.1.0.1 |  | Merge invoices in draft
[account_invoice_payment_retention](account_invoice_payment_retention/) | 16.0.1.0.0 |  | Account Invoice Payment Retention
[account_invoice_payment_term_date_due](account_invoice_payment_term_date_due/) | 16.0.1.0.0 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Display invoices date due when using payment terms
[account_invoice_pricelist](account_invoice_pricelist/) | 16.0.1.0.2 |  | Add partner pricelist on invoices
[account_invoice_pricelist_sale](account_invoice_pricelist_sale/) | 16.0.1.0.0 |  | Module to fill pricelist from sales order in invoice.
[account_invoice_recipient_bank_currency](account_invoice_recipient_bank_currency/) | 16.0.1.0.0 |  | Module to fill recipient bank from invoices by using the invoice's currency.
[account_invoice_refund_code](account_invoice_refund_code/) | 16.0.1.0.0 |  | This module allows to have specific refund codes.
[account_invoice_refund_line_selection](account_invoice_refund_line_selection/) | 16.0.1.0.0 |  | This module allows the user to refund specific lines in a invoice
[account_invoice_refund_link](account_invoice_refund_link/) | 16.0.1.0.4 |  | Show links between refunds and their originator invoices.
[account_invoice_refund_reason](account_invoice_refund_reason/) | 16.0.1.0.1 | [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Account Invoice Refund Reason.
[account_invoice_refund_reason_skip_anglo_saxon](account_invoice_refund_reason_skip_anglo_saxon/) | 16.0.1.0.0 | [![ChrisOForgeFlow](https://github.com/ChrisOForgeFlow.png?size=30px)](https://github.com/ChrisOForgeFlow) | Account Invoice Refund Reason.
[account_invoice_section_sale_order](account_invoice_section_sale_order/) | 16.0.1.0.0 |  | For invoices targetting multiple sale order addsections with sale order name.
[account_invoice_show_currency_rate](account_invoice_show_currency_rate/) | 16.0.1.0.3 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Show currency rate in invoices.
[account_invoice_supplier_ref_unique](account_invoice_supplier_ref_unique/) | 16.0.1.0.0 |  | Checks that supplier invoices are not entered twice
[account_invoice_supplier_self_invoice](account_invoice_supplier_self_invoice/) | 16.0.1.0.0 |  | Purchase Self Invoice
[account_invoice_supplierinfo_update](account_invoice_supplierinfo_update/) | 16.0.1.1.0 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | In the supplier invoice, automatically updates all products whose unit price on the line is different from the supplier price
[account_invoice_supplierinfo_update_discount](account_invoice_supplierinfo_update_discount/) | 16.0.1.0.0 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | In the supplier invoice, automatically update all products whose discount on the line is different from the supplier discount
[account_invoice_supplierinfo_update_triple_discount](account_invoice_supplierinfo_update_triple_discount/) | 16.0.1.0.1 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | In the supplier invoice, automatically update all products whose discounts on the line is different from the supplier discounts
[account_invoice_tax_note](account_invoice_tax_note/) | 16.0.1.0.0 |  | Print tax notes on customer invoices
[account_invoice_tax_required](account_invoice_tax_required/) | 16.0.1.1.0 |  | This module adds functional a check on invoice to force user to set tax on invoice line.
[account_invoice_transmit_method](account_invoice_transmit_method/) | 16.0.1.0.2 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Configure invoice transmit method (email, post, portal, ...)
[account_invoice_tree_currency](account_invoice_tree_currency/) | 16.0.1.0.0 |  | Show currencies in the invoice tree view
[account_invoice_triple_discount](account_invoice_triple_discount/) | 16.0.1.0.3 |  | Manage triple discount on invoice lines
[account_mail_autosubscribe](account_mail_autosubscribe/) | 16.0.1.0.1 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Automatically subscribe partners to their company's invoices
[account_menu_invoice_refund](account_menu_invoice_refund/) | 16.0.1.0.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | New invoice menu that combine invoices and refunds
[account_move_auto_post_ref](account_move_auto_post_ref/) | 16.0.1.0.1 | [![rafaelbn](https://github.com/rafaelbn.png?size=30px)](https://github.com/rafaelbn) [![yajo](https://github.com/yajo.png?size=30px)](https://github.com/yajo) | Propagate customer ref when auto-generating next recurring invoice
[account_move_cancel_confirm](account_move_cancel_confirm/) | 16.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Account Move Cancel Confirm
[account_move_substate](account_move_substate/) | 16.0.1.0.1 |  | Account Move Sub State
[account_move_tier_validation](account_move_tier_validation/) | 16.0.1.0.0 |  | Extends the functionality of Account Moves to support a tier validation process.
[account_receipt_journal](account_receipt_journal/) | 16.0.1.1.0 | [![eLBati](https://github.com/eLBati.png?size=30px)](https://github.com/eLBati) [![anddago78](https://github.com/anddago78.png?size=30px)](https://github.com/anddago78) | Define and use journals dedicated to receipts
[account_receipt_send](account_receipt_send/) | 16.0.1.0.2 | [![Shide](https://github.com/Shide.png?size=30px)](https://github.com/Shide) | Send receipts
[account_tax_change](account_tax_change/) | 16.0.1.0.3 | [![sebalix](https://github.com/sebalix.png?size=30px)](https://github.com/sebalix) | Configure your tax changes starting from a date.
[account_tax_group_widget_base_amount](account_tax_group_widget_base_amount/) | 16.0.1.0.0 | [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) | Adds base amount to tax group widget
[account_tax_one_vat](account_tax_one_vat/) | 16.0.1.0.0 |  | Allow only the selection of one VAT Tax.
[account_tax_one_vat_purchase](account_tax_one_vat_purchase/) | 16.0.1.0.0 |  | Allow only the selection of one VAT Tax in purchase order line
[partner_invoicing_mode](partner_invoicing_mode/) | 16.0.2.0.0 |  | Base module for handling multiple partner invoicing mode
[partner_invoicing_mode_at_shipping](partner_invoicing_mode_at_shipping/) | 16.0.1.2.0 |  | Create invoices automatically when goods are shipped.
[partner_invoicing_mode_monthly](partner_invoicing_mode_monthly/) | 16.0.2.0.0 |  | Create invoices automatically on a monthly basis.
[portal_account_personal_data_only](portal_account_personal_data_only/) | 16.0.1.0.0 |  | Portal Accounting Personal Data Only
[product_form_account_move_line_link](product_form_account_move_line_link/) | 16.0.1.0.0 |  | Adds a button on product forms to access Journal Items
[purchase_invoicing_no_zero_line](purchase_invoicing_no_zero_line/) | 16.0.1.0.0 |  | Avoid creation of zero quantity invoice lines from purchase
[purchase_stock_picking_return_invoicing](purchase_stock_picking_return_invoicing/) | 16.0.1.0.2 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) [![MiquelRForgeFlow](https://github.com/MiquelRForgeFlow.png?size=30px)](https://github.com/MiquelRForgeFlow) | Add an option to refund returned pickings
[sale_line_refund_to_invoice_qty](sale_line_refund_to_invoice_qty/) | 16.0.1.0.0 |  | Allow deciding whether refunded quantity should be considered as quantity to reinvoice
[sale_order_invoicing_grouping_criteria](sale_order_invoicing_grouping_criteria/) | 16.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | Sales order invoicing grouping criteria
[sale_order_invoicing_qty_percentage](sale_order_invoicing_qty_percentage/) | 16.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | Sales order invoicing by percentage of the quantity
[sale_timesheet_invoice_description](sale_timesheet_invoice_description/) | 16.0.1.0.0 |  | Add timesheet details in invoice line
[stock_picking_invoicing](stock_picking_invoicing/) | 16.0.1.0.0 |  | Stock Picking Invoicing
[stock_picking_return_refund_option](stock_picking_return_refund_option/) | 16.0.1.0.1 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Update the refund options in pickings

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
