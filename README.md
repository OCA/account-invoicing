
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
[account_invoice_blocking](account_invoice_blocking/) | 16.0.1.0.1 |  | Set a blocking (No Follow-up) flag on invoices
[account_invoice_change_currency](account_invoice_change_currency/) | 16.0.1.0.1 | [![luisg123v](https://github.com/luisg123v.png?size=30px)](https://github.com/luisg123v) [![rolandojduartem](https://github.com/rolandojduartem.png?size=30px)](https://github.com/rolandojduartem) | Allows to change currency of Invoice by wizard
[account_invoice_check_total](account_invoice_check_total/) | 16.0.1.0.0 |  | Check if the verification total is equal to the bill's total
[account_invoice_currency_taxes](account_invoice_currency_taxes/) | 16.0.1.0.1 |  | Taxes in company currency in invoice report
[account_invoice_fiscal_position_update](account_invoice_fiscal_position_update/) | 16.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Changing the fiscal position of an invoice will auto-update invoice lines
[account_invoice_merge](account_invoice_merge/) | 16.0.1.0.1 |  | Merge invoices in draft
[account_invoice_pricelist](account_invoice_pricelist/) | 16.0.1.0.0 |  | Add partner pricelist on invoices
[account_invoice_pricelist_sale](account_invoice_pricelist_sale/) | 16.0.1.0.0 |  | Module to fill pricelist from sales order in invoice.
[account_invoice_refund_line_selection](account_invoice_refund_line_selection/) | 16.0.1.0.0 |  | This module allows the user to refund specific lines in a invoice
[account_invoice_refund_link](account_invoice_refund_link/) | 16.0.1.0.3 |  | Show links between refunds and their originator invoices.
[account_invoice_supplierinfo_update](account_invoice_supplierinfo_update/) | 16.0.1.0.1 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | In the supplier invoice, automatically updates all products whose unit price on the line is different from the supplier price
[account_invoice_tax_required](account_invoice_tax_required/) | 16.0.1.0.0 |  | This module adds functional a check on invoice to force user to set tax on invoice line.
[account_invoice_transmit_method](account_invoice_transmit_method/) | 16.0.1.0.1 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Configure invoice transmit method (email, post, portal, ...)
[account_invoice_tree_currency](account_invoice_tree_currency/) | 16.0.1.0.0 |  | Show currencies in the invoice tree view
[account_invoice_triple_discount](account_invoice_triple_discount/) | 16.0.1.0.1 |  | Manage triple discount on invoice lines
[account_menu_invoice_refund](account_menu_invoice_refund/) | 16.0.1.0.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | New invoice menu that combine invoices and refunds
[account_move_tier_validation](account_move_tier_validation/) | 16.0.1.0.0 |  | Extends the functionality of Account Moves to support a tier validation process.
[account_receipt_journal](account_receipt_journal/) | 16.0.1.1.0 | [![eLBati](https://github.com/eLBati.png?size=30px)](https://github.com/eLBati) [![anddago78](https://github.com/anddago78.png?size=30px)](https://github.com/anddago78) | Define and use journals dedicated to receipts
[account_receipt_send](account_receipt_send/) | 16.0.1.0.2 | [![Shide](https://github.com/Shide.png?size=30px)](https://github.com/Shide) | Send receipts
[account_tax_change](account_tax_change/) | 16.0.1.0.1 | [![sebalix](https://github.com/sebalix.png?size=30px)](https://github.com/sebalix) | Configure your tax changes starting from a date.
[account_tax_group_widget_base_amount](account_tax_group_widget_base_amount/) | 16.0.1.0.0 | [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) | Adds base amount to tax group widget
[partner_invoicing_mode](partner_invoicing_mode/) | 16.0.1.0.1 |  | Base module for handling multiple partner invoicing mode
[partner_invoicing_mode_at_shipping](partner_invoicing_mode_at_shipping/) | 16.0.1.0.1 |  | Create invoices automatically when goods are shipped.
[partner_invoicing_mode_monthly](partner_invoicing_mode_monthly/) | 16.0.1.0.1 |  | Create invoices automatically on a monthly basis.
[purchase_stock_picking_return_invoicing](purchase_stock_picking_return_invoicing/) | 16.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) [![MiquelRForgeFlow](https://github.com/MiquelRForgeFlow.png?size=30px)](https://github.com/MiquelRForgeFlow) | Add an option to refund returned pickings
[sale_line_refund_to_invoice_qty](sale_line_refund_to_invoice_qty/) | 16.0.1.0.0 |  | Allow deciding whether refunded quantity should be considered as quantity to reinvoice
[sale_order_invoicing_grouping_criteria](sale_order_invoicing_grouping_criteria/) | 16.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | Sales order invoicing grouping criteria
[stock_picking_return_refund_option](stock_picking_return_refund_option/) | 16.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Update the refund options in pickings

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
