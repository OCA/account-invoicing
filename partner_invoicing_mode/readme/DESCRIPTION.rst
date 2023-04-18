This is a base module for implementing different invoicing mode for customers.
It adds a selection field `invoicing_mode` in the Accounting tab of the partner
with a default value (Odoo standard invoicing mode).
But it serves no purpose installed on its own.

The following modules use it to install specific invoicing mode :

    * `partner_invoicing_mode_at_shipping`
    * `partner_invoicing_mode_monthly`
