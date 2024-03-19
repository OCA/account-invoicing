This is a base module for implementing different invoicing mode for customers.
It adds a selection field `invoicing_mode` in the Accounting tab of the partner
with a default value (Odoo standard invoicing mode).

It can be used on its own to generate automatically (e.g.: each day)
the invoices for standard invoicing mode.

The following modules use it to install specific invoicing mode :

    * `partner_invoicing_mode_at_shipping`
    * `partner_invoicing_mode_monthly`
    * `partner_invoicing_mode_weekly`
